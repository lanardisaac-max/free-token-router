# Free Token Router: bounded fallback candidate

This repository contains an authenticated, text-only fallback API. It does not extend the ChatGPT/Codex application allowance, resume those apps automatically, or certify an autonomous coding executor. Free provider allowances are finite. Railway hosting is separate from inference pricing. Never promise uninterrupted service, unlimited tokens or guaranteed savings.

## Release status — 2026-10-17

The existing production service was observed online, but working authenticated inference was not verified. Its older code permitted unauthenticated requests, paid/prohibited routes and misleading health reporting. This candidate replaces those routes and is not live until its exact reviewed commit is deployed and independently verified.

| Route | Candidate status | Activation evidence required |
| --- | --- | --- |
| Groq Free Plan / `openai/gpt-oss-20b` | Implemented, offline tested | Secure key, actual Free Plan/no paid billing, model/license/data-policy qualification, live bounded text test |
| OpenRouter / `openai/gpt-oss-20b:free`, Groq only | Optional, disabled | Fresh exact free endpoint/provider evidence, account/key/policy qualification; public endpoints API returned an empty list on Oct 17 |
| OpenAI API, Anthropic/Claude, Cohere trial, Antigravity | Excluded | No activation path in this app |

`openai/gpt-oss-20b` is an open-weight model served by Groq; the router does not call OpenAI's paid API. The optional OpenRouter route pins both model and provider, disables provider fallback and sets a zero prompt/completion price ceiling. Since it selects Groq, it is not independent of a Groq infrastructure outage. Do not count it as a second proven inference provider.

## Enforced controls

- Bearer authentication with a separately provisioned token of at least 32 characters, checked before reading request bodies. Only `/` and `/health` are public. Keys never appear in responses.
- Fixed HTTPS endpoints; no caller-selected URLs, providers or model names. Redirects and environment proxies disabled. Unknown fields, tools, streaming, images and legacy protocols are rejected.
- Maximum 32 KiB request, 32 messages, 1,024 output tokens and 128 KiB upstream response. Entire request deadline defaults to 15 seconds and cannot exceed 30. Groq uses the current `max_completion_tokens` parameter and fixed low reasoning. Each provider is attempted at most once; no retry loop or paid spillover.
- One concurrent inference request per process. Default three-second interval between new requests. A second attempt for the same request can bypass that interval but still consumes the daily reservation.
- SQLite reservations before every upstream attempt, including failed attempts: hard ceilings of 40 attempts and 40,000 conservative token-reservation units per UTC day. Output limit plus serialized UTF-8 input bytes plus 512 overhead units are reserved; these are a conservative local proxy, not measured provider billable tokens. Provider account limits remain authoritative and may be lower.
- Durable volume required and explicitly confirmed. Missing/unwritable state fails closed. Reservations and provider cooldowns survive restart only if that volume remains intact. Deploy exactly one replica and worker; the process lock and host-local SQLite do not implement a distributed quota service. Do not delete/reset state to regain allowance.
- Rate limits and transient failures cool the provider using bounded `Retry-After` or 60 seconds. Authentication, payment and permission errors stop the request and disable that provider for 24 hours. No raw provider errors, prompts or secrets in application logs.
- `/health` means the process is alive. Authenticated `/ready` reports configuration/budget/cooldown eligibility only and always returns `inference_verified:false`. Neither is operational certification.
- Legacy `/v1/messages` and `/v1/completions` return 410 after authentication. Automatic cross-project integration scripts exit without work; old mutation workflows are removed. No hosted Actions workflow is added.

## Contract

`POST /v1/chat/completions`, with `Authorization: Bearer <router-token>`:

```json
{"model":"free-text","messages":[{"role":"user","content":"A nonsensitive text request"}],"max_tokens":128,"stream":false}
```

Only `model`, `messages`, `max_tokens`, `stream:false`, and optional `temperature` are accepted. Messages use nonempty string content and `system`, `user`, or `assistant` roles. The normalized reply has `object:chat.completion`, `model:free-text` and one assistant text choice. Unsupported contracts fail explicitly rather than silently losing tool/system information. Application errors contain a local request ID and sanitized code; 429/503 include `Retry-After`. Retain unfinished work locally; do not treat timeouts as a successful completion or blindly replay external side effects.

This is not a Responses API or tool-calling implementation. Do not point Codex/Work/production tools at it and claim compatibility. A separate authorized client adapter and end-to-end tool-call/reply test would be required. Human text use and automated coding acceptance are separate gates.

## Verify locally

In an authorized isolated cloud checkout, using Python 3.11+:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

All tests use HTTPX MockTransport and synthetic keys. They make no paid or live inference requests. Do not run installations on an unqualified native disk. No test result is proof of a live free account, working key, deployed commit, or billing configuration.

## Safe release and rollback

1. Independently review the exact candidate commit and full test result. Preserve the current deployment/source identity and rollback option. Do not merge the unrelated shared-memory pointer draft as a prerequisite.
2. Through an already authorized normal provider session, verify Groq Free Plan, zero paid billing exposure, applicable Apache 2.0 model license and account/data policy. Provision a scoped provider key into the secret store without printing it; create a separate strong router token there. Do not reuse unrelated service tokens or enable auto-reload. If no authorized session/key is available, record that exact blocker and keep this candidate undeployed.
3. Verify an existing durable volume and cost authorization, then configure `.env.example` names with real secrets only in the secret store. `*_CONFIRMED=true` are operator assertions, not automatic account verification. Old `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `COHERE_API_KEY` and `LLM_ROUTER_BASE_URL` do not enable this code. Remove unused keys separately through an authorized secret-management operation after consumer inventory; never expose their values.
4. Deploy the reviewed commit to the existing router service, one replica/worker. Do not deploy a disabled replacement and call it available. No broad integration/production client changes are part of this release.
5. Verify unauthenticated inference is rejected, liveness works, readiness is authenticated, and a single nonsensitive authenticated request returns the expected text/schema within the deadline. Verify the actual provider/account usage remains free. Record timestamp, exact commit/deployment, request ID, model and outcome, never key/prompt/private response content.
6. Verify persistent caps across a controlled restart and quota-failure behavior in an isolated test environment. Qualify a separate client only if its protocol and isolation gates are authorized. If release fails, stop routing new work; use the retained deployment/source rollback only within applicable authority. Never restore the old unauthenticated/prohibited routes merely to make health green.

## Consumption and recovery policy

Keep ChatGPT as PM. Routine checks should use ordinary reasoning where configurable; reserve expensive reasoning and parallel workers for changed, difficult work. Reuse exact-head passing evidence, fetch small deltas and bounded logs, stop unchanged checks early, and never rerun an unresolved denied route. Preserve existing schedules unless separately changed by the owner. Prompt policy is advisory enforcement by the executor, not a platform-wide token ceiling.

When actual remaining allowance is visible through an authorized interface, checkpoint at 20%; at 10%, defer nonessential investigation; at 5%, stop noncritical fan-out and preserve the final handoff. If remaining usage cannot be read, mark it unknown, keep work bounded, and do not invent a balance. No automatic credit purchase or paid fallback. These thresholds are an operating policy, not an installed platform alert or global kill switch.

Before yielding or changing providers, use [HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md) in the existing authorized project evidence path. Preserve exact source and scope leases; record completed checks and remaining gates. Never hand credentials, customer data or entire chat histories to a free provider. A fallback can draft/reason over approved nonsensitive text while application access is exhausted; it cannot automatically take over protected tooling or ongoing production operations.

## Source evidence checked 2026-10-17

- [Groq rate limits](https://console.groq.com/docs/rate-limits): finite organization/model RPM/RPD/TPM/TPD, account console controls actual limits.
- [Groq data policy](https://console.groq.com/docs/your-data): review retention/exceptions and ZDR before sensitive use.
- [OpenRouter free model](https://openrouter.ai/openai/gpt-oss-20b:free): zero token price and Apache 2.0 model listing, not proof of active endpoint capacity.
- [OpenRouter exact endpoints](https://openrouter.ai/api/v1/models/openai/gpt-oss-20b:free/endpoints): returned `endpoints:[]` in the public read; optional route remains unqualified.
- [OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection): exact provider restriction, disabled fallbacks and price caps.
- [Cohere pricing](https://cohere.com/pricing): trial keys are not for production/commercial usage.

Historical implementation and claims remain in git history. The current README supersedes the older integration/deployment guides. Do not revive retired instructions from copied checklists.
