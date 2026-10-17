# Candidate verification — 2026-10-17

Baseline: `7088fa5b3e5e63cc77c65d3a519067c946a7ccfa` on `master`.
Scope: this repository only. No runtime checkout or reconstruction of other project scopes; no live inference, credential access, cross-project integration, deployment or new hosted CI.

Root checks: full `python -m pytest -q -p no:cacheprovider`, 43 passed; Python compilation and `git diff --check` passed. Tests exercise the real ASGI app with synthetic credentials and HTTPX provider-boundary transport. Meaningful failures were observed before implementing the absent contract and guards. No network calls are required by the suite.

Independent read-only review by `/root/fallback_source_audit` reproduced three malformed-input failures (non-ASCII bearer header, extreme numeric temperature, lone-surrogate text); each has a regression test and now fails safely. The reviewer also verified persistent reservations, cooldown/deadline behavior and the corrected minimum readiness budget. The final Groq output-cap mapping was also independently reviewed. Reviewer full suite: 43 passed in 0.60 seconds. Reviewed SHA-256: app.py `d4b9a9843927ba399c88a4f0c61ef38e8296b75c4881109f79c2a9e37cf9c6c2`; tests/test_router.py `b3ab2b1b3a3003e912a9e9dca8bcfd8aaf6681e7f5de6a5bc8a394ea86878156`; README.md `079c989a8cbb62245dacfeb388d2edf268100234e5b340ca763af436528d6c71`. Root rechecked all three hashes before commit.

## Operational evidence and unproven gates

The existing Railway service `free-token-router` in production was read on Oct 17: deployment `7b21b1e6-8b24-4511-b552-7bc41ccc936e` remains the July 20 successful deployment, tracking `master`, one configured replica, no staged changes, no volumes. Observed variable names: `COHERE_API_KEY`, `LLM_ROUTER_BASE_URL`, `OPENAI_API_KEY`. Values were not read; names do not establish valid keys or inference. The new code is not deployed by this validation.

Missing activation evidence: Groq Free Plan/no-paid-billing and data/license qualification; securely provisioned provider key and separate router token; authorized durable volume for quota state; exact-reviewed deployment plus live bounded text acceptance. OpenRouter public exact free-model endpoints returned `[]`; this is not working fallback capacity. No new account, key, paid plan, credit purchase or volume was created.

Do not call this operational backup completion, ChatGPT/Codex app continuity, or 42-repository memory certification. No shared-memory acceptance numerator changed here. Existing Antigravity retirement, prohibited-provider rules and protected project scopes remain binding.
