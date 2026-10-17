"""HTTP boundary tests; all provider I/O uses MockTransport, never real keys."""
import asyncio
import json
import time

import httpx
import pytest

import app as module

AUTH = {"Authorization": "Bearer " + "s" * 40}
REQUEST = {"model": "free-text", "messages": [{"role": "system", "content": "Be precise"}, {"role": "user", "content": "Hello"}], "max_tokens": 128}


def answer(model="openai/gpt-oss-20b"):
    return {"id": "provider-id", "object": "chat.completion", "model": model, "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hello back"}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13}}


@pytest.fixture
def env(monkeypatch, tmp_path):
    for key in ["ROUTER_AUTH_TOKEN", "GROQ_API_KEY", "GROQ_FREE_PLAN_CONFIRMED", "OPENROUTER_API_KEY", "OPENROUTER_FREE_CONFIRMED", "OPENROUTER_PROVIDER", "ROUTER_TOTAL_TIMEOUT_SECONDS", "ROUTER_DAILY_REQUEST_LIMIT", "ROUTER_DAILY_TOKEN_LIMIT"]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("ROUTER_AUTH_TOKEN", "s" * 40)
    monkeypatch.setenv("ROUTER_STATE_PATH", str(tmp_path / "budget.sqlite3"))
    monkeypatch.setenv("ROUTER_STATE_DURABLE_CONFIRMED", "true")
    monkeypatch.setenv("GROQ_API_KEY", "test-groq")
    monkeypatch.setenv("GROQ_FREE_PLAN_CONFIRMED", "true")
    monkeypatch.setenv("ROUTER_MIN_INTERVAL_SECONDS", "0")


def make_app(handler):
    # Baseline has only a global app; exercise its real HTTP behavior for RED.
    factory = getattr(module, "create_app", None)
    return factory(transport=httpx.MockTransport(handler)) if factory else module.app


def run(handler, method="POST", path="/v1/chat/completions", body=None, headers=AUTH):
    async def exercise():
        app = make_app(handler)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://router") as client:
            return await client.request(method, path, content=json.dumps(REQUEST if body is None else body, ensure_ascii=True).encode(), headers=headers)
    return asyncio.run(exercise())


def forbidden(_):
    pytest.fail("request must not reach a provider")


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer wrong"}])
def test_auth_rejected_before_provider(env, headers):
    assert run(forbidden, headers=headers).status_code == 401


def test_paid_and_prohibited_keys_cannot_enable_routing(env, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY")
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "COHERE_API_KEY"]:
        monkeypatch.setenv(key, "must-ignore")
    assert run(forbidden).status_code == 503


def test_free_account_requires_explicit_confirmation(env, monkeypatch):
    monkeypatch.delenv("GROQ_FREE_PLAN_CONFIRMED")
    assert run(forbidden).status_code == 503


@pytest.mark.parametrize("extra", [{"model": "gpt-4o"}, {"model": "anthropic/claude"}, {"stream": True}, {"tools": []}, {"max_tokens": 99999}, {"messages": []}, {"max_tokens": True}])
def test_invalid_or_unsupported_request_rejected_pre_network(env, extra):
    assert run(forbidden, body={**REQUEST, **extra}).status_code == 400


def test_success_preserves_messages_and_standard_response(env):
    def provider(req):
        assert req.url.host == "api.groq.com"
        data = json.loads(req.content)
        assert data["messages"] == REQUEST["messages"]
        assert data["model"] == "openai/gpt-oss-20b"
        return httpx.Response(200, json=answer())
    r = run(provider)
    assert r.status_code == 200
    assert r.json()["model"] == "free-text"
    assert r.json()["choices"][0]["message"]["content"] == "Hello back"
    assert r.headers["x-request-id"]


def test_rate_limit_fails_over_then_skips_cooling_provider(env, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-or")
    monkeypatch.setenv("OPENROUTER_FREE_CONFIRMED", "true")
    monkeypatch.setenv("OPENROUTER_PROVIDER", "Groq")
    calls = []
    def provider(req):
        calls.append(req.url.host)
        if req.url.host == "api.groq.com":
            return httpx.Response(429, headers={"Retry-After": "120"})
        data = json.loads(req.content)
        assert data["model"].endswith(":free")
        assert data["provider"] == {"only": ["Groq"], "allow_fallbacks": False, "data_collection": "deny", "max_price": {"prompt": 0, "completion": 0}}
        return httpx.Response(200, json=answer("openai/gpt-oss-20b:free"))
    async def exercise():
        app = make_app(provider)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://router") as c:
            assert (await c.post("/v1/chat/completions", json=REQUEST, headers=AUTH)).status_code == 200
            assert (await c.post("/v1/chat/completions", json=REQUEST, headers=AUTH)).status_code == 200
    asyncio.run(exercise())
    assert calls == ["api.groq.com", "openrouter.ai", "openrouter.ai"]


def test_openrouter_arbitrary_provider_not_admitted(env, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-or")
    monkeypatch.setenv("OPENROUTER_FREE_CONFIRMED", "true")
    monkeypatch.setenv("OPENROUTER_PROVIDER", "Anthropic")
    assert run(forbidden).status_code == 503


@pytest.mark.parametrize("status", [400, 401, 402, 403])
def test_non_retryable_failure_does_not_forward_to_another_provider(env, monkeypatch, status):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-or")
    monkeypatch.setenv("OPENROUTER_FREE_CONFIRMED", "true")
    monkeypatch.setenv("OPENROUTER_PROVIDER", "Groq")
    calls = []
    def provider(req):
        calls.append(str(req.url))
        return httpx.Response(status, text="SECRET_PROVIDER_ERROR")
    r = run(provider)
    assert r.status_code in (400, 503)
    assert len(calls) == 1
    assert "SECRET" not in r.text


@pytest.mark.parametrize("data", [{}, {"choices": []}, {"choices": [{"message": {"role": "assistant", "content": None}}]}, {**answer(), "model": "anthropic/claude"}])
def test_malformed_or_wrong_model_upstream_not_accepted(env, data):
    r = run(lambda _: httpx.Response(200, json=data))
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "providers_unavailable"


def test_deadline_cancels_slow_upstream(env, monkeypatch):
    monkeypatch.setenv("ROUTER_TOTAL_TIMEOUT_SECONDS", "0.05")
    async def slow(_):
        await asyncio.sleep(1)
        return httpx.Response(200, json=answer())
    start = time.monotonic()
    assert run(slow).status_code == 503
    assert time.monotonic() - start < .5


def test_daily_request_cap_blocks_without_provider_call(env, monkeypatch):
    monkeypatch.setenv("ROUTER_DAILY_REQUEST_LIMIT", "1")
    calls = []
    def provider(req):
        calls.append(req)
        return httpx.Response(200, json=answer())
    async def exercise():
        app = make_app(provider)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://router") as c:
            first = await c.post("/v1/chat/completions", json=REQUEST, headers=AUTH)
            second = await c.post("/v1/chat/completions", json=REQUEST, headers=AUTH)
            assert first.status_code == 200
            assert second.status_code == 429
            assert int(second.headers["Retry-After"]) > 0
    asyncio.run(exercise())
    assert len(calls) == 1


def test_daily_token_reservation_cap_blocks_pre_network(env, monkeypatch):
    monkeypatch.setenv("ROUTER_DAILY_TOKEN_LIMIT", "100")
    assert run(forbidden).status_code == 429


def test_readiness_is_not_liveness_or_operational_proof(env, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY")
    assert run(forbidden, "GET", "/health").status_code == 200
    r = run(forbidden, "GET", "/ready")
    assert r.status_code == 503
    assert r.json()["inference_verified"] is False


@pytest.mark.parametrize("path", ["/v1/messages", "/v1/completions"])
def test_legacy_routes_retired_without_upstream(env, path):
    assert run(forbidden, path=path).status_code == 410


def test_interval_does_not_prevent_same_request_failover(env, monkeypatch):
    monkeypatch.setenv("ROUTER_MIN_INTERVAL_SECONDS", "3")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-or")
    monkeypatch.setenv("OPENROUTER_FREE_CONFIRMED", "true")
    monkeypatch.setenv("OPENROUTER_PROVIDER", "Groq")
    def provider(req):
        return httpx.Response(503) if req.url.host == "api.groq.com" else httpx.Response(200, json=answer("openai/gpt-oss-20b:free"))
    assert run(provider).status_code == 200


def test_budget_survives_app_restart_and_readiness_reports_exhaustion(env, monkeypatch):
    monkeypatch.setenv("ROUTER_DAILY_REQUEST_LIMIT", "1")
    assert run(lambda _: httpx.Response(200, json=answer())).status_code == 200
    assert run(forbidden).status_code == 429
    assert run(forbidden, "GET", "/ready").status_code == 503


def test_missing_durable_budget_fails_closed(env, monkeypatch):
    monkeypatch.delenv("ROUTER_STATE_DURABLE_CONFIRMED")
    assert run(forbidden).status_code == 503


def test_oversize_request_rejected_without_provider_call(env):
    body = {**REQUEST, "messages": [{"role": "user", "content": "x" * 40000}]}
    assert run(forbidden, body=body).status_code == 413


def test_oversize_upstream_rejected(env):
    data = answer()
    data["choices"][0]["message"]["content"] = "x" * 140000
    assert run(lambda _: httpx.Response(200, json=data)).status_code == 503


def test_concurrent_request_rejected_without_duplicate_inference(env):
    async def exercise():
        entered, release = asyncio.Event(), asyncio.Event()
        async def provider(_):
            entered.set()
            await release.wait()
            return httpx.Response(200, json=answer())
        app = make_app(provider)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://router") as c:
            first = asyncio.create_task(c.post("/v1/chat/completions", json=REQUEST, headers=AUTH))
            await asyncio.wait_for(entered.wait(), 1)
            second = await c.post("/v1/chat/completions", json=REQUEST, headers=AUTH)
            release.set()
            assert (await first).status_code == 200
            assert second.status_code == 429
            assert second.json()["error"]["code"] == "router_busy"
    asyncio.run(exercise())


def test_openrouter_has_zero_price_ceiling(env, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-or")
    monkeypatch.setenv("OPENROUTER_FREE_CONFIRMED", "true")
    monkeypatch.setenv("OPENROUTER_PROVIDER", "Groq")
    def provider(req):
        assert json.loads(req.content)["provider"]["max_price"] == {"prompt": 0, "completion": 0}
        return httpx.Response(200, json=answer("openai/gpt-oss-20b:free"))
    assert run(provider).status_code == 200


def test_retired_integrator_dry_run_cannot_modify_target(tmp_path):
    import subprocess
    import sys
    sentinel = tmp_path / "app.py"
    sentinel.write_text("unchanged")
    result = subprocess.run([sys.executable, "skill_implementation.py", "--path", str(tmp_path), "--dry-run"], capture_output=True, text=True)
    assert result.returncode == 2
    assert "retired" in result.stderr.lower()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["app.py"]
    assert sentinel.read_text() == "unchanged"


def test_deadline_cools_provider_before_next_request(env, monkeypatch):
    monkeypatch.setenv("ROUTER_TOTAL_TIMEOUT_SECONDS", "0.05")
    async def slow(_):
        await asyncio.sleep(1)
        return httpx.Response(200, json=answer())
    assert run(slow).status_code == 503
    assert run(forbidden).status_code == 503


def test_non_ascii_configured_token_fails_closed(env, monkeypatch):
    monkeypatch.setenv("ROUTER_AUTH_TOKEN", "é" * 40)
    assert run(forbidden).status_code == 401


def test_non_ascii_supplied_bearer_is_unauthorized(env):
    assert run(forbidden, headers=[(b"authorization", b"Bearer \xff")]).status_code == 401


def test_extreme_json_number_is_bad_input(env):
    assert run(forbidden, body={**REQUEST, "temperature": 10 ** 1000}).status_code == 400


def test_lone_surrogate_content_is_bad_input(env):
    body = {**REQUEST, "messages": [{"role": "user", "content": "\ud800"}]}
    assert run(forbidden, body=body).status_code == 400


def test_readiness_requires_minimum_request_budget(env, monkeypatch):
    monkeypatch.setenv("ROUTER_DAILY_TOKEN_LIMIT", "100")
    assert run(forbidden, "GET", "/ready").status_code == 503


def test_groq_uses_current_completion_cap_and_low_reasoning(env):
    def provider(req):
        data = json.loads(req.content)
        assert data["max_completion_tokens"] == REQUEST["max_tokens"]
        assert "max_tokens" not in data
        assert data["reasoning_effort"] == "low"
        return httpx.Response(200, json=answer())
    assert run(provider).status_code == 200
