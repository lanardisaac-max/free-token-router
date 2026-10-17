#!/usr/bin/env python3
"""Authenticated, bounded text fallback. No paid or prohibited API routes."""
import asyncio
from contextlib import closing
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json
import math
import os
import secrets
import sqlite3
import time
import uuid

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

MODEL = "free-text"
UPSTREAM_MODEL = "openai/gpt-oss-20b"
MAX_BODY = 32768
MAX_RESPONSE = 131072


def number(name, default, low, high):
    try:
        value = float(os.getenv(name, str(default)))
        return value if math.isfinite(value) and low <= value <= high else default
    except ValueError:
        return default


def error(status, code, request_id, retry=None):
    headers = {"X-Request-ID": request_id, "Cache-Control": "no-store"}
    if retry is not None:
        headers["Retry-After"] = str(max(1, math.ceil(retry)))
    return JSONResponse({"error": {"code": code, "message": "Request not completed; retain your local work and retry after the indicated delay.", "request_id": request_id}}, status_code=status, headers=headers)


class Budget:
    """SQLite metadata only. Reservations survive process restart on durable storage."""
    def __init__(self, path):
        self.path = path
        self.limit = int(number("ROUTER_DAILY_REQUEST_LIMIT", 40, 1, 40))
        self.tokens = int(number("ROUTER_DAILY_TOKEN_LIMIT", 40000, 1, 40000))
        self.interval = number("ROUTER_MIN_INTERVAL_SECONDS", 3, 0, 3600)
        with closing(self.connect()) as db:
            db.executescript("CREATE TABLE IF NOT EXISTS budget(day TEXT PRIMARY KEY, requests INTEGER NOT NULL, tokens INTEGER NOT NULL); CREATE TABLE IF NOT EXISTS cooldown(provider TEXT PRIMARY KEY, until REAL NOT NULL);")

    def connect(self):
        return sqlite3.connect(self.path, timeout=.1, isolation_level=None)

    def available(self, provider):
        with closing(self.connect()) as db:
            row = db.execute("SELECT until FROM cooldown WHERE provider=?", (provider,)).fetchone()
        return max(0, (row[0] if row else 0) - time.time())

    def cool(self, provider, seconds):
        with closing(self.connect()) as db:
            db.execute("INSERT INTO cooldown VALUES (?, ?) ON CONFLICT(provider) DO UPDATE SET until=MAX(until,excluded.until)", (provider, time.time() + seconds))

    def remaining(self, minimum):
        day = datetime.now(timezone.utc).date().isoformat()
        with closing(self.connect()) as db:
            row = db.execute("SELECT requests,tokens FROM budget WHERE day=?", (day,)).fetchone()
        requests, used = row or (0, 0)
        return requests < self.limit and used + minimum <= self.tokens and self.available("global") <= 0

    def reserve(self, tokens, *, same_request=False):
        now = datetime.now(timezone.utc)
        day = now.date().isoformat()
        reset = 86400 - (now.hour * 3600 + now.minute * 60 + now.second)
        with closing(self.connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO budget VALUES (?,0,0)", (day,))
            requests, used = db.execute("SELECT requests,tokens FROM budget WHERE day=?", (day,)).fetchone()
            row = db.execute("SELECT until FROM cooldown WHERE provider='global'").fetchone()
            if not same_request and row and row[0] > time.time():
                db.execute("ROLLBACK")
                return row[0] - time.time()
            if requests >= self.limit or used + tokens > self.tokens:
                db.execute("ROLLBACK")
                return reset
            db.execute("UPDATE budget SET requests=requests+1,tokens=tokens+? WHERE day=?", (tokens, day))
            db.execute("INSERT INTO cooldown VALUES ('global',?) ON CONFLICT(provider) DO UPDATE SET until=excluded.until", (time.time() + self.interval,))
            db.execute("DELETE FROM budget WHERE day < ?", (day,))
            db.execute("COMMIT")
        return 0


def retry_seconds(value):
    try:
        seconds = float(value)
        return min(86400, max(1, seconds)) if math.isfinite(seconds) else 60
    except (ValueError, TypeError):
        try:
            return min(86400, max(1, parsedate_to_datetime(value).timestamp() - time.time()))
        except (ValueError, TypeError, OverflowError):
            return 60


def validate(body):
    if not isinstance(body, dict) or set(body) - {"model", "messages", "max_tokens", "stream", "temperature"}:
        return None
    if body.get("model") != MODEL or body.get("stream", False) is not False:
        return None
    messages, limit = body.get("messages"), body.get("max_tokens", 512)
    if type(limit) is not int or not 1 <= limit <= 1024 or not isinstance(messages, list) or not 1 <= len(messages) <= 32:
        return None
    for m in messages:
        if not isinstance(m, dict) or set(m) != {"role", "content"} or m["role"] not in ("system", "user", "assistant") or not isinstance(m["content"], str) or not m["content"].strip():
            return None
    try:
        json.dumps(messages, ensure_ascii=False).encode("utf-8")
    except UnicodeError:
        return None
    temperature = body.get("temperature", 0.2)
    if type(temperature) not in (int, float) or not 0 <= temperature <= 2 or not math.isfinite(temperature):
        return None
    return {"messages": messages, "max_tokens": limit, "temperature": temperature, "stream": False}


def normalize(data, request_id, allowed_model):
    if not isinstance(data, dict) or data.get("model") not in allowed_model:
        return None
    choices = data.get("choices")
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
        return None
    choice = choices[0]
    message = choice.get("message")
    if not isinstance(message, dict) or message.get("role") != "assistant" or not isinstance(message.get("content"), str) or not message["content"].strip() or message.get("tool_calls"):
        return None
    if choice.get("finish_reason") not in ("stop", "length"):
        return None
    result = {"id": "chatcmpl-" + request_id, "object": "chat.completion", "created": int(time.time()), "model": MODEL, "choices": [{"index": 0, "message": {"role": "assistant", "content": message["content"]}, "finish_reason": choice["finish_reason"]}]}
    usage = data.get("usage")
    if isinstance(usage, dict) and all(type(usage.get(k)) is int and usage[k] >= 0 for k in ("prompt_tokens", "completion_tokens", "total_tokens")):
        result["usage"] = {k: usage[k] for k in ("prompt_tokens", "completion_tokens", "total_tokens")}
    return result


def create_app(*, transport=None):
    api = FastAPI(title="Free Token Router", docs_url=None, redoc_url=None, openapi_url=None)
    token = os.getenv("ROUTER_AUTH_TOKEN", "")
    if not token.isascii():
        token = ""
    providers = []
    if os.getenv("GROQ_API_KEY") and os.getenv("GROQ_FREE_PLAN_CONFIRMED") == "true":
        providers.append(("groq", "https://api.groq.com/openai/v1/chat/completions", os.environ["GROQ_API_KEY"], UPSTREAM_MODEL))
    # Fixed free model and reviewed provider only. Never auto/random/paid routing.
    if os.getenv("OPENROUTER_API_KEY") and os.getenv("OPENROUTER_FREE_CONFIRMED") == "true" and os.getenv("OPENROUTER_PROVIDER") == "Groq":
        providers.append(("openrouter", "https://openrouter.ai/api/v1/chat/completions", os.environ["OPENROUTER_API_KEY"], UPSTREAM_MODEL + ":free"))
    path = os.getenv("ROUTER_STATE_PATH")
    budget = None
    if path and os.getenv("ROUTER_STATE_DURABLE_CONFIRMED") == "true":
        try:
            budget = Budget(path)
        except (sqlite3.Error, OSError):
            pass  # Fail closed; health reveals only readiness, never paths or secrets.
    total_timeout = number("ROUTER_TOTAL_TIMEOUT_SECONDS", 15, .05, 30)
    minimum_request = len(json.dumps({"messages": [{"role": "user", "content": "x"}], "max_tokens": 1, "temperature": 0, "stream": False}).encode()) + 513
    busy = asyncio.Lock()

    def configured():
        return len(token) >= 32 and budget is not None and bool(providers)

    @api.middleware("http")
    async def guard(request, call_next):
        request_id = uuid.uuid4().hex
        request.state.request_id = request_id
        if request.url.path not in ("/", "/health"):
            supplied = request.headers.get("authorization", "")
            if len(token) < 32 or not supplied.isascii() or not secrets.compare_digest(supplied, "Bearer " + token):
                return error(401, "unauthorized", request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["Cache-Control"] = "no-store"
        return response

    @api.get("/")
    async def index():
        return {"service": "free-token-router", "version": "2", "contract": "bounded text only; no coding-client certification"}

    @api.get("/health")
    async def health():
        return {"status": "alive", "inference_verified": False}

    @api.get("/ready")
    async def ready():
        try:
            eligible = configured() and budget.remaining(minimum_request) and any(budget.available(p[0]) <= 0 for p in providers)
        except sqlite3.Error:
            eligible = False
        return JSONResponse({"configured": configured(), "eligible": bool(eligible), "inference_verified": False}, status_code=200 if eligible else 503)

    @api.get("/v1/models")
    async def models():
        return {"object": "list", "data": [{"id": MODEL, "object": "model", "owned_by": "router"}] if configured() else []}

    @api.post("/v1/messages")
    @api.post("/v1/completions")
    async def retired(request: Request):
        return error(410, "legacy_contract_retired", request.state.request_id)

    @api.post("/v1/chat/completions")
    async def chat(request: Request):
        rid = request.state.request_id
        if busy.locked():
            return error(429, "router_busy", rid, 3)
        async with busy:
            try:
                async with asyncio.timeout(total_timeout):
                    raw = bytearray()
                    async for chunk in request.stream():
                        raw.extend(chunk)
                        if len(raw) > MAX_BODY:
                            return error(413, "request_too_large", rid)
                    try:
                        body = validate(json.loads(raw))
                    except (ValueError, UnicodeError, RecursionError):
                        body = None
                    if body is None:
                        return error(400, "unsupported_request", rid)
                    if not configured():
                        return error(503, "not_configured", rid, 60)
                    # Conservative reservation per attempt, no refunds after failure.
                    reserve = len(json.dumps(body, ensure_ascii=False).encode()) + body["max_tokens"] + 512
                    retry = 60
                    async with httpx.AsyncClient(transport=transport, follow_redirects=False, trust_env=False, timeout=min(7, total_timeout)) as client:
                        attempted = False
                        for name, url, key, model in providers:
                            wait = budget.available(name)
                            if wait > 0:
                                retry = max(retry, wait)
                                continue
                            wait = budget.reserve(reserve, same_request=attempted)
                            if wait > 0:
                                return error(429, "local_budget_exhausted", rid, wait)
                            attempted = True
                            payload = {**body, "model": model}
                            if name == "groq":
                                payload["max_completion_tokens"] = payload.pop("max_tokens")
                                payload["reasoning_effort"] = "low"
                            if name == "openrouter":
                                payload["provider"] = {"only": ["Groq"], "allow_fallbacks": False, "data_collection": "deny", "max_price": {"prompt": 0, "completion": 0}}
                            try:
                                async with client.stream("POST", url, json=payload, headers={"Authorization": "Bearer " + key}) as response:
                                    if response.status_code != 200:
                                        if response.status_code in (401, 402, 403):
                                            budget.cool(name, 86400)
                                            return error(503, "provider_configuration_required", rid, 86400)
                                        if response.status_code in (400, 404, 422):
                                            return error(400, "provider_rejected_request", rid)
                                        wait = retry_seconds(response.headers.get("Retry-After"))
                                        budget.cool(name, wait)
                                        retry = max(retry, wait)
                                        continue
                                    content = bytearray()
                                    async for chunk in response.aiter_bytes():
                                        content.extend(chunk)
                                        if len(content) > MAX_RESPONSE:
                                            break
                                    result = normalize(json.loads(content), rid, (model, UPSTREAM_MODEL)) if len(content) <= MAX_RESPONSE else None
                                    if result:
                                        return JSONResponse(result)
                                    budget.cool(name, 60)
                            except asyncio.CancelledError:
                                budget.cool(name, 60)
                                raise
                            except (httpx.HTTPError, ValueError, UnicodeError, RecursionError):
                                budget.cool(name, 60)
                    return error(503, "providers_unavailable", rid, retry)
            except TimeoutError:
                return error(503, "request_deadline_exceeded", rid, 60)
            except sqlite3.Error:
                return error(503, "budget_store_unavailable", rid, 60)

    return api


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")), workers=1, access_log=False)
