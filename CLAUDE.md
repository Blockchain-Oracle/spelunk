# CLAUDE.md — Spelunk

Spelunk — an **agentic SOC copilot packaged as a native Splunk app** with a generative-UI chat cockpit. A SOC analyst asks security questions in natural language; an agent generates SPL, runs it on Splunk data, classifies threats (MITRE), forecasts escalation (CDTSM), and drafts a triage note — each step rendered as a typed React component in the chat stream. Built on Splunk's own AI surfaces.

**Read first:** `STATE.md` (pivot history + current status), then `docs/PLAN.md` (full system design + phasing). Grounding reports in `docs/research/`.

## How to work

1. **Spike before architecture.** The next real step is **Phase 0** in `docs/PLAN.md`: a throwaway `restmap.conf` hello-world REST handler on a local Splunk Enterprise trial to resolve 4 unverified unknowns (handler registration, streaming-vs-buffering through the splunkd Web proxy, proxy timeout, bundled-monitor auto-index). Do NOT commit to the transport design until this is answered.
2. **Build inside-out, in the plan's phase order** (§4): spike → scaffold/rebrand → agent brain (`spelunk_core`) → data → cockpit → Splunk-native shapes → MCP → gated layers → package.
3. **Research before implementing.** If unsure how a library/API behaves, check Context7 MCP first, then the verified corpus, then read the actual source. The spec can be wrong — verify before coding.
4. **Reuse the archived patterns.** The prior project (proven Splunk app build pipeline, SimpleXML mount, KV-store confs, AppInspect harness, Next.js landing) lives at `../splunk/archive/splunkgate-v1/aegis/`. Copy patterns from there; don't reinvent.
5. **Verify before claiming done.** Run it. Lighter testing posture (smoke tests + manual e2e), not a mock-heavy suite.

## Hard rules

- **Every source file ≤ 400 LOC** (non-blank, non-comment).
- **No custom authentication anywhere.** Splunk is the identity provider; the cockpit inherits the Splunk session same-origin; gated AI tokens live in `passwords.conf` (setup-time). The website is static — no backend, no auth.
- **Agent logic lives in `packages/spelunk_core`** (importable, CI-testable). `apps/splunk_app/.../bin/` files are **thin wrappers** only (they run under Splunk's embedded Python and can't be imported in CI). `spelunk_core` is vendored into `bin/` at package time.
- **Gated AI via the `providers.py` abstraction.** Pipeline must run end-to-end on a generic OpenAI-compatible model alone. Splunk Hosted Models / SAIA plug in by config when entitlement is granted. **Never claim a self-hosted/local model is Splunk-hosted** — that was the v1 mistake. Self-hosted Foundation-Sec is fine ONLY with a transparent README disclosure.
- `ruff` clean. No `verify=False` in production HTTP. No real credentials in code or fixtures.
- The cockpit↔agent transport is **polling-first**; streaming is an upgrade only if the Phase-0 spike proves bytes flush through the proxy. The React `event.type`→component registry is identical either way.
- `ui-contract/src/events.ts` is **hand-synced** to `spelunk_core/events.py` — keep them identical.

## Repo map

- `packages/spelunk_core/` — Python agent (agent, pipeline, providers, events, spl). The brain.
- `packages/ui-contract/` — shared TS step-event union (generative-UI registry key).
- `apps/splunk_app/spelunk_app/` — the installable Splunk app (`bin/`, `default/*.conf`, cockpit view, lookups, manifest).
- `apps/cockpit/` — React SPA → webpack → the app's `appserver/static/spelunk/`.
- `apps/landing/` — static marketing+docs (reuse archived Next.js, rebranded).
- `data/` — synthetic `spelunk:auth` event generator.
- `docs/` — `PLAN.md` + `research/`. `tooling/` — SLIM packaging + AppInspect.

## Rewarded Splunk AI surfaces (the whole point)

Python SDK AI (`splunklib.ai`) · Splunk MCP Server (consumer) · AI Assistant SAIA (`saia_generate_spl`) · Hosted Models (Foundation-Sec / gpt-oss via `| ai`) · CDTSM (`| apply CDTSM`). Confirmed-accessible core = Python SDK AI + MCP Server; the rest is entitlement-gated and plugs in via `providers.py`.

## Git

Repo: `github.com/Blockchain-Oracle/spelunk` (public, `main`). Conventional commits. Don't commit unless asked.
