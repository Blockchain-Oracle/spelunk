# Spelunk — Agentic SOC Copilot (native Splunk app + generative-UI cockpit)

## Context

We spent ~10 days building "SplunkGate" — a runtime AI safety-net — then read the hackathon brief from first principles and found it used **none** of the five rewarded Splunk AI surfaces and misread "Agentic Ops." We are pivoting to **Spelunk**: an agentic SOC copilot that does real operational work *on* Splunk data, packaged as a native Splunk app whose UI lives inside Splunk Web. Grounded in two fact-checked research reports (`workspace/research/2026-06-13-*.md`), the verified domain corpus (`workspace/context/`), our own archived working app (`archive/splunkgate-v1/aegis/splunk_apps/splunkgate_app/` already proves React→webpack→SimpleXML mount + SplunkJS works), and an independent system-architecture pass.

**Locked decisions:** Name = **Spelunk**. Track = **Security-primary** (ADR-013: Security $3K + Developer Tools $1K + MCP Server stretch $1K; Hosted Models pivotable). Gated AI = **provider abstraction**, real models wired by config when the Cisco entitlement email (sent, 2-day SLA) unlocks them; honest self-hosted fallback, never claimed as Splunk-hosted. Website = **static marketing+docs only**. Judging = **both** a clean installable `.tgz` + demo video AND a hosted Splunk instance with judge login.

---

## 0. Immediate next action (THIS session — scoped, not the full build)

The cloud Ultraplan planner failed because the only GitHub repo it can see is the old, messy SplunkGate one (buried under `archive/`). It has no clean ground truth for the Spelunk structure. **So the single task this session is to give it that ground truth:**

1. Create a fresh **public** GitHub repo `Blockchain-Oracle/spelunk` (`gh repo create`).
2. Scaffold the clean monorepo per §1d — **full**: every folder, every config file (`package.json`, `pyproject.toml`, `app.conf`, `commands.conf`, `restmap.conf`, `collections.conf`, etc.), `README.md` + `STATE.md` (explaining the SplunkGate→Spelunk pivot), this plan, and both research reports under `docs/`, plus **stub source files whose docstrings state each module's intent** (so the planner sees the exact intended shape).
3. `git init` → commit (conventional) → push to `main`.
4. Report the repo URL so the cloud Ultraplan can clone it and plan against real, correct structure.

This is **scaffold + push only** — NOT implementing the pipeline/cockpit/agent. The cloud planner (and our subsequent build) takes it from there with full GitHub information. The sections below are the blueprint the scaffold encodes.

---

## 1. System Design (decided before any file)

### 1a. Authentication — there is NO custom auth anywhere
- **Cockpit (in Splunk Web):** user is already authenticated by Splunk. Cockpit JS calls the same-origin proxy path `/splunkd/__raw/services/spelunk/...`; Splunk attaches the session cookie + `X-Splunk-Form-Key` CSRF automatically. *(SPIKE: confirm exact path + CSRF auto-send from a mounted view.)*
- **Agent → Splunk data (MCP):** Splunk Bearer token with `mcp_tool_execute`, provisioned once at setup, stored encrypted in `passwords.conf`.
- **Hosted Models / SAIA:** Splunk Cloud tenant entitlement (`list_tokens_scs` role) — tenant-level, no per-user auth.
- **Self-hosted LLM fallback:** endpoint + optional API key in `passwords.conf` (encrypted), setup-time.
- **Website:** static, no auth, no backend.
- **Hosted judging instance:** uses Splunk's **own native login**. We provision the instance, install Spelunk, ingest data, create a judge account via Splunk RBAC. This is an ops checklist (see §5), not auth code.

### 1b. Data model
- **Index** `spelunk_security`, **sourcetype** `spelunk:auth` (JSON, `INDEXED_EXTRACTIONS=json` — proven in archive `props.conf`).
- **Event shape (what a SOC analyst queries):** `_time, user, src_ip, dest_host, action(success|failure), auth_method, event_type(login|privilege_escalation|file_access), failure_count, geo_country, user_agent, mitre_technique_id, mitre_tactic_id, risk_score, event_id`.
- **Triage history:** **KV Store** collection (`collections.conf` + `transforms.conf external_type=kvstore`), keyed `_key=event_id` — mutable notes read/written by both agent and alert action. (Not a summary index — append-only is wrong for mutable notes.)
- **MITRE mapping:** reuse `lookups/atlas_technique_mapping.csv` (AI-on-AI events) + add an ATT&CK enterprise CSV (`technique_id`→name,tactic) for SOC events; both wired as file lookups in `transforms.conf`, exported in `metadata/default.meta`.

### 1c. End-to-end user flow (first principles)
1. Analyst opens **Spelunk** in Splunk Web → cockpit view loads (React mounted via SimpleXML).
2. Types a NL question: *"failed logins from new countries this week — is this an attack, and will it continue?"*
3. Cockpit POSTs the question to `bin/chat_handler.py` (same-origin, Splunk session).
4. The agent pipeline runs as **discrete short steps**, each emitting a typed step-event the cockpit renders immediately:
   - `spl` → SAIA `saia_generate_spl` (or LLM) writes SPL → `<SplBlock onRun>` with a Run button.
   - `results` → SPL executed (MCP `splunk_run_query` or SplunkJS `SearchManager`) → `<ResultsTable>`.
   - `classification` → Foundation-Sec maps findings → MITRE technique → `<MitreCard>`.
   - `forecast` → CDTSM forecasts escalation/volume → `<ForecastChart>`.
   - `narrative` → gpt-oss writes the analyst summary → `<Narrative>`.
5. Analyst can click Run on the SPL, drill into results (SplunkJS), or accept the triage note → written to KV Store.
- **Splunk-native entry points besides the cockpit:** `| spelunk "<question>"` custom search command; a custom **alert action** that auto-triages a notable event and writes the note to KV Store.

### 1d. Monorepo topology (best-practice, ≤400 LOC/file)
**pnpm workspaces for TS + a single flat `uv` project for Python** (one Python package → no uv workspace needed).
```
spelunk/
├── packages/
│   ├── spelunk_core/                 # importable, pytest-able Python (runs in CI, vendored into app at package time)
│   │   ├── agent.py                  # builds splunklib.ai.Agent
│   │   ├── pipeline.py               # SPL→run→classify→forecast→narrate, as discrete short steps
│   │   ├── providers.py              # LLMProvider: SplunkHosted | SelfHosted | External (config-driven)
│   │   ├── events.py                 # the wire contract (step-event union) — source of truth
│   │   └── spl.py                    # SPL helpers
│   └── ui-contract/                  # TS: the step-event discriminated union, hand-synced to events.py
├── apps/
│   ├── splunk_app/spelunk_app/       # the packaged .tgz
│   │   ├── bin/                      # THIN wrappers: chat_handler.py, spelunk_command.py, triage_alert_action.py, tools.py
│   │   ├── default/                  # app.conf commands.conf alert_actions.conf restmap.conf web.conf collections.conf
│   │   │   └── data/ui/{views/cockpit.xml, nav/default.xml}
│   │   ├── appserver/static/spelunk/cockpit.js   # built bundle (committed)
│   │   ├── lookups/                  # atlas + att&ck CSVs
│   │   ├── metadata/default.meta  META-INF/manifest.json
│   │   └── scripts/run_appinspect.sh + .appinspect.*   # reuse harness
│   ├── cockpit/                      # React SPA → webpack (externals React/ReactDOM, ts-loader) → app static/
│   │   ├── cockpit.tsx  components/{MitreCard,ForecastChart,SplBlock,ResultsTable,Narrative}.tsx  styles/tokens.css
│   └── landing/                      # reuse archived Next.js web/, rebranded, static export
├── data/                             # synthetic generator (reuse Synthetic-Data/), retargeted to spelunk:auth
├── docs/                             # PRD, architecture, ADRs
└── tooling/                          # SLIM packaging, CI
```
- **Python split rationale:** `bin/` runs under Splunk's embedded Python (can't import in CI). So agent logic lives in importable `spelunk_core` (unit-tested in CI), vendored into `bin/` at package time; `bin/` files are thin wrappers. Mirrors the archive's `splunkgate_core` + thin-app split.
- **Shared types:** `ui-contract` is hand-synced to `events.py` (codegen is over-engineering for 3 days). This union is the generative-UI registry key.

### 1e. Cockpit ↔ agent transport (the riskiest piece — de-risked by design)
- **Endpoint:** custom REST handler via `restmap.conf` + `PersistentServerConnectionApplication` in `bin/chat_handler.py` — runs in `splunkd`, inherits session, reads gated tokens server-side.
- **Build POLLING FIRST (safe default):** `POST /chat/start` → `job_id`; cockpit issues sequential `GET /chat/step?job_id&cursor`; server stashes step state in KV Store. **Streaming (SSE/chunked) is an upgrade attempted only after the spike confirms bytes flush through the splunkd Web proxy.** The React component registry is **identical** either way (pure client switch on `event.type`).
- **Timeout mitigation (independent of spike):** `pipeline.py` is decomposed into discrete short per-step invokes from day one, so no single request holds the connection near the proxy ceiling. (`splunklib.ai AgentLimits` default 600s, but the Web proxy ceiling is lower and unverified.)

---

## 2. Rewarded-surface coverage (every component traces to a named surface)

| Surface | Use | Accessible now? |
|---|---|---|
| Python SDK AI (`splunklib.ai`) | agent core in `spelunk_core`, run from `bin/` | ✅ Enterprise trial |
| Splunk MCP Server (app 7931) | agent consumes `splunk_run_query` etc. | ✅ install on Enterprise |
| AI Assistant (SAIA) | `saia_generate_spl` via MCP | 🟡 gated on email |
| Hosted Models (Foundation-Sec / gpt-oss) | `\| ai provider=splunk_hosted` via provider abstraction | 🟡 gated; self-hosted fallback |
| Hosted Models (CDTSM) | `\| apply CDTSM` (AITK 5.7.3+ on-prem preview) | 🟡 install & test |

Confirmed-shippable core = Python SDK AI + MCP Server (2 surfaces at runtime). All else plugs in via config without rework — exactly what `providers.py` exists for.

---

## 3. Reuse vs build new
**Reuse (from `archive/splunkgate-v1/aegis/`):** `web/` landing (rebrand) · `splunk_apps/splunkgate_app/src/` webpack+mount pattern · SimpleXML view pattern · `collections.conf`/`transforms.conf` KV-store pattern · AppInspect harness · `lookups/atlas_technique_mapping.csv` · `Synthetic-Data/` generators · webpack/tsconfig toolchain.
**Build new:** `spelunk_core/{agent,pipeline,providers,events,spl}.py` · `bin/{chat_handler,spelunk_command,triage_alert_action,tools}.py` · cockpit `.tsx` + 5 components · `ui-contract` · rebranded landing copy · `spelunk:auth` synthetic generator.

---

## 4. Phasing — SPIKE FIRST, then build inside-out

**Phase 0 — Day-1 spike (resolves 4 unknowns before committing).** Stand up a local Splunk Enterprise free trial. Deploy a hello-world `restmap.conf` handler that writes `data:`, sleeps 2s, writes again. `curl -N` it through the Web proxy (8000) with a session cookie. Confirm: (1) handler base-class + `python.version` registration, (2) whether bytes stream or buffer (→ decides streaming vs polling), (3) the proxy request timeout, (4) a bundled `[monitor]` input auto-indexes on enable. Also confirm `spelunk_core` vendoring onto `sys.path` under embedded Python.
**Phase 1 — Monorepo scaffold + rebrand.** pnpm + uv workspaces; `spelunk_app` skeleton from archived patterns; rebrand `landing`.
**Phase 2 — Agent brain (`spelunk_core`).** `agent.py`+`pipeline.py`+`providers.py`+`events.py`, runnable from a CLI against a generic OpenAI-compatible model (no Splunk needed). Smoke-tested in CI.
**Phase 3 — Data.** `spelunk:auth` synthetic generator; bundled `[monitor]` seed input + HEC path; KV Store collection; MITRE lookups.
**Phase 4 — Cockpit (demo star).** `bin/chat_handler.py` (polling) + React generative UI; mounts in Splunk Web; renders the 5 component types.
**Phase 5 — Splunk-native shapes.** `| spelunk` search command + triage alert action.
**Phase 6 — MCP integration.** consume official Splunk MCP Server (Bearer token, `splunk_run_query`).
**Phase 7 — Wire gated layers.** flip `providers.py` to Hosted Models / SAIA when email unlocks; install AITK 5.7.3+ and test `apply CDTSM`. Streaming upgrade if Phase-0 spike was green.
**Phase 8 — Package + polish.** `.tgz` via SLIM, AppInspect green, demo video, landing/docs final, provision hosted judging instance.

---

## 5. Hosted judging instance — ops checklist (not code)
Provision a Splunk instance (Cloud trial or hosted Enterprise) → install Spelunk `.tgz` → enable bundled monitor input (data self-loads) → create a `judge` role/user via Splunk RBAC → verify cockpit + `| spelunk` + alert action work → share URL + judge credentials. Native Splunk login; no custom auth.

## 6. Testing posture (lighter than v1, per Abu)
Smoke tests only: `spelunk_core` pipeline happy path + provider selection (CI, real generic LLM), one search-command test, AppInspect green. Real services in the hot path; manual end-to-end in a live Splunk install. No 183-test mock-heavy suite.

## 7. Verification (end-to-end)
- `ruff` clean; `pytest -q` (small suite) green; AppInspect green.
- Install `.tgz` in local Splunk → open Spelunk → ask a security question → SPL + results + MitreCard + ForecastChart + Narrative render as components.
- `| spelunk "show failed logins from new countries this week"` returns agent output in SPL.
- Saved search triggers → alert action writes a note to KV Store.
- MCP client lists `splunk_*` tools; agent calls `splunk_run_query` live.
- Email unlocks → flip `spelunk.conf` provider → re-run same flow against real Foundation-Sec / CDTSM; record for Hosted Models bonus.

## 8. Open risks (carried, with mitigations)
1. Custom-handler streaming through the splunkd proxy **unverified** → polling-first; streaming is an upgrade.
2. Proxy request timeout possibly < 600s → per-step short invokes regardless.
3. `restmap.conf` handler registration / `python.version` unverified → Phase-0 hello-world.
4. Bundled `[monitor]` auto-index unverified on hosted instance → Phase-0 test.
5. Gated AI depends on pending email → pipeline must run end-to-end on `splunklib.ai` + generic OpenAI-compatible model alone.
6. `spelunk_core` vendoring onto embedded-Python `sys.path` unverified → Phase-0.

## 9. Out of scope (cut from v1, kept in `archive/` for UI reference only)
Safety-net middleware, judges, DefenseClaw/Cisco AI Defense regex, the custom `splunkgate_mcp` server, the 183-test suite, the "verdict" domain model, any web auth / hosted backend / hosted demo.
