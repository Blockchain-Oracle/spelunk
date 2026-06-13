# Pivot Research — Splunk Agentic Ops Hackathon
**Date:** 2026-06-13
**Goal:** ground the architecture decision in the actual surface area Splunk ships, NOT improvised guesses. All claims cite a verified URL, a path inside a cloned repo, or a quote from the existing verified domain corpus at `workspace/context/`.

Cloned-repo root for this pass: `/tmp/splunk-research/`. Existing prior research that this pass builds on (do NOT re-derive — already verified): `workspace/context/06-splunk-ai-stack/01..08*.md`, `workspace/context/02-agent-frameworks/06-splunklib-ai-deep-read.md`, and `workspace/research/splunk-agentic-ops-2026/13-architecture-recommendation-v2.md`.

---

## 1. Executive summary — the hard facts

1. **Splunk Hosted Models are Splunk Cloud Platform paid-customer only.** Verbatim from the Feb 18 2026 launch blog: "generally available for Splunk Cloud Platform customers." No free-trial mention. No developer-license mention. (Re-verified live via WebFetch 2026-06-13.)
2. **The exact `provider=` syntax for Hosted Models in `| ai` is still NOT in any public doc page.** WebFetch on `5.7.4` `about-the-ai-command` lists providers verbatim as "OpenAI, Gemini, Bedrock, Groq, and Ollama" — Hosted Models option is mentioned in 5.7.0 release notes but the SPL invocation syntax is not surfaced to public docs. **Unverified** without a live Cloud tenant. (Also flagged in `context/06-splunk-ai-stack/04-hosted-models.md:47`.)
3. **The official Splunk MCP Server (Splunkbase app 7931) is closed-source.** `CiscoDevNet/Splunk-MCP-Server-official` is README + LICENSE only — confirmed by clone (`/tmp/splunk-research/Splunk-MCP-Server-official/`: 2 files, 3 commits all from 2026-02-18). You cannot register tools into it; you can only run a parallel MCP server.
4. **The MCP Server runs INSIDE Splunk** at `https://<host>:8089/services/mcp` over HTTP/SSE, auth via `Authorization: Bearer <encrypted_token>`. Requires Splunk RBAC capabilities `mcp_tool_execute` (+ `mcp_tool_admin` for token mgmt). On the official server: 10 native `splunk_*` tools, plus 4 `saia_*` tools when SAIA is co-installed. (Verified in `context/06-splunk-ai-stack/03-splunk-mcp-server.md`.)
5. **`splunklib.ai` 3.0.0 ships REAL working sample apps.** All three sample apps named in the brief exist in `splunk-sdk-python/examples/`: `ai_custom_alert_app/`, `ai_custom_search_app/`, `ai_modinput_app/`. Cloned 2026-06-13. Code excerpts in Track 2 below.
6. **`splunklib.ai` is LangChain-only under the hood.** `splunklib/ai/core/backend_registry.py:18-24` hard-codes `langchain_backend_factory`. The provider classes are `OpenAIModel`, `AnthropicModel`, `GoogleModel` — no built-in "Splunk Hosted Model" class. To target Hosted Models from inside `splunklib.ai`, you currently have no first-class path; you'd point `OpenAIModel(base_url=...)` at a tenant endpoint (URL undocumented).
7. **SAIA has no public REST API.** Its only programmatic surface is the 4 `saia_*` MCP tools that appear when Splunk MCP Server + SAIA app 7245 are co-installed. SAIA is Splunk Cloud-only ("Via Cloud Connected" on Enterprise — i.e. federation, not local). Agent Mode (SAIA 2.0, Apr 2026) is gated to Cloud, AWS regions only, not FedRAMP. (`context/06-splunk-ai-stack/02-saia-ai-assistant-for-spl.md`.)
8. **The "native AI cockpit for Splunk" wedge ONLY works end-to-end on a paid Splunk Cloud tenant.** All three hosted-model entitlements + SAIA + MCP Server install paths converge on Cloud. The free Splunk Enterprise trial gets you: `splunklib.ai` (any LLM provider you bring your own key for), `| ai` against external providers (OpenAI/Ollama/Bedrock etc.), and you can run your own MCP server alongside. You do NOT get Foundation-Sec / gpt-oss / CDTSM hosted; you do NOT get SAIA; you do NOT get the official Splunk MCP Server's `saia_*` tools.
9. **The credible prior-art is small and the bar is set.** Build-a-thon 2025 winners (DNS Guard AI, CIMplicity AI) used Splunk-native ML (MLTK `fit DensityFunction` / `fit KMeans`), packaged as proper Splunkbase apps, NOT chat UIs. Judges rewarded "Splunk-native, app-shaped, AppInspect-friendly" over "webapp with LLM." (Verified in `research/splunk-agentic-ops-2026/05-prior-patterns.md` Pattern 1 + 6, and `13-architecture-recommendation-v2.md` fact 19.)
10. **The hackathon registered-team gallery already shows entries** (e.g. `gongahkia/splunk-agentic-ops-hackathon-2026`, `chalithah/splunk-claude-mcp-agent`). The MCP-bridge-to-Claude-Desktop pattern is already taken — duplicating it = low novelty. (WebSearch 2026-06-13.)

---

## 2. Track 1 — Splunk MCP Server (consumer pattern)

### Official server
- Splunkbase app 7931 ("Splunk MCP Server" by Splunk LLC) — current 1.2.0, May 27 2026. Closed-source TGZ.
- GitHub `CiscoDevNet/Splunk-MCP-Server-official` cloned to `/tmp/splunk-research/Splunk-MCP-Server-official/`. Contains only `LICENSE` + `README.md`. The README documents the consumer protocol verbatim — full quotes already saved in `context/06-splunk-ai-stack/03-splunk-mcp-server.md` lines 134-204.
- Transport: HTTP/SSE, endpoint `https://<host>:8089/services/mcp`, protocol version `2025-03-26`, capabilities: `{"tools": {}}` only — NO `resources`/`prompts`.
- Auth: `Authorization: Bearer <encrypted_token>`. Splunk-issued token. **Required Splunk capabilities: `mcp_tool_execute`** (`mcp_tool_admin` for issuing tokens).
- Native tools (10): `splunk_run_query`, `splunk_get_info`, `splunk_get_indexes`, `splunk_get_index_info`, `splunk_get_metadata`, `splunk_get_user_info`, `splunk_get_user_list`, `splunk_get_kv_store_collections`, `splunk_get_knowledge_objects`, `splunk_run_saved_search` (beta).
- SAIA tools (4, only when SAIA app 7245 is co-installed): `saia_generate_spl`, `saia_explain_spl`, `saia_optimize_spl`, `saia_ask_splunk_question`.

### Minimum consumer code — Claude Desktop / Claude Code
Verbatim from the CiscoDevNet README (preserved at `context/sources/docs-saved/ciscodevnet-splunk-mcp-server-official-README.md`):

```json
{
  "mcpServers": {
    "splunk-mcp-server": {
      "command": "npx",
      "args": ["-y", "mcp-remote",
        "https://<SPLUNK_HOST>:8089/services/mcp",
        "--header", "Authorization: Bearer <YOUR_TOKEN>"],
      "env": {"NODE_TLS_REJECT_UNAUTHORIZED": "0"}
    }
  }
}
```

### Minimum consumer code — Python agent
The official server has no Python client SDK example in the repo. The `splunklib.ai` SDK auto-discovers the Splunk MCP Server alongside via `splunklib/ai/tools.py` (file is ~300 lines per deep-read; line 308 disables TLS — see `context/02-agent-frameworks/06-splunklib-ai-deep-read.md` fact 10). Any FastMCP / `mcp` Python client can call the endpoint with the same Bearer header.

### Does it need a real Splunk instance?
**Yes.** The MCP Server is a Splunkbase app installed on a Search Head. No standalone process. Need either:
- Paid Splunk Cloud Platform tenant (where v1.2.0 is GA), OR
- Splunk Enterprise install + Splunkbase install + free Splunk Enterprise trial license (10GB/day, 60 days). The app's Splunkbase compat list includes Enterprise 9.3–10.4, so the trial path is viable for the MCP Server itself — but NOT for SAIA (Cloud-only) and NOT for Hosted Models (Cloud-only). (`context/06-splunk-ai-stack/02-saia-ai-assistant-for-spl.md:65-69`.)

### Community alternatives (cloned this pass)
- `splunk/splunk-mcp-server2` — `/tmp/splunk-research/splunk-mcp-server2/`. FastMCP-based, 509 lines `python/server.py`. Ships `guardrails.py` (SPL-risk scoring, output sanitization). Apache-2.0. **Same author org as the official one, but explicitly "Unofficial."** Has tools `validate_spl`, `search_oneshot`, etc. — good reference for guardrail patterns.
- `deslicer/mcp-for-splunk` — `/tmp/splunk-research/mcp-for-splunk/`. FastMCP-based, 1267-line `src/server.py`, 20+ tools, 16 resources, ITSI MCP add-on (`mcp_itsi/`), workflow specialists (`examples/workflow_runner_demo.py`, etc.). Apache-2.0. **The single richest community starting point** if we wanted to start from a working FastMCP base.
- `chalithah/splunk-claude-mcp-agent` — `/tmp/splunk-research/splunk-claude-mcp-agent/`. 222-line `splunk_mcp.py`. Simple Splunk Enterprise → Claude Desktop bridge. Documented as registered hackathon entry. Pattern is taken.

---

## 3. Track 2 — Python SDK AI (packaging an agent inside a Splunk app)

Cloned `splunk/splunk-sdk-python` to `/tmp/splunk-research/splunk-sdk-python/`. SDK 3.0.0 (PyPI 2026-05-12) introduced `splunklib/ai/`. Working tree shows `3.0.1a0` in `pyproject.toml`. Full code-level deep-read already exists at `context/02-agent-frameworks/06-splunklib-ai-deep-read.md` — do NOT reread, use as source of truth.

### Three sample apps — all real, all read this pass

#### `ai_custom_search_app` — custom search command `| agenticreport`
Files (5):
- `bin/agentic_reporting_csc.py` (150 lines)
- `bin/setup_logging.py`
- `default/app.conf`
- `default/commands.conf` (4 lines — see below)
- `metadata/local.meta`

`default/commands.conf` (verbatim, all 4 lines):
```ini
[agenticreport]
filename = agentic_reporting_csc.py
chunked = true
python.required = 3.13
```

`bin/agentic_reporting_csc.py:130-147` shows the canonical pattern — `Agent(...) async context manager` driving an `EventingCommand`:
```python
async with Agent(
    model=OpenAIModel(model="gpt-4o-mini",
                       base_url="https://api.openai.com/v1",
                       api_key="<super_secret_key>"),
    system_prompt="You are an Expert Splunk Data Analyst.",
    service=self.service,
    output_schema=AgentOutput,
) as agent:
    result = await agent.invoke_with_data(
        instructions=f'Decide if this record matches the intent: "{self.should_filter}". Is it relevant to "{self.highlight_topic}"?',
        data=dict(record),
    )
    return result.structured_output
```

#### `ai_custom_alert_app` — custom alert action `threat_level_assessment.py`
Files: `bin/threat_level_assessment.py` (159 lines), `bin/log_server.py`, `default/{savedsearches,alert_actions,app,inputs}.conf`, `README.md`. Reads alert results from gzip CSV, calls `Agent(...)` with a `Literal["high","low"]`-typed Pydantic schema, writes assessment back to a Splunk index via `service.indexes[output_index].submit(...)`. (Lines 87-99, 140-152.)

#### `ai_modinput_app` — modular input `agentic_weather.py`
Files: `bin/agentic_weather.py` (155 lines), `default/{app,inputs}.conf`, `README/inputs.conf.spec`, `weather.csv`. Subclasses `splunklib.modularinput.script.Script`, emits enriched events via `EventWriter`.

### How to ship "a Splunk app that opens to a chat UI calling an LLM"

The sample apps do NOT include a chat UI. They are all backend search/alert/modinput commands. **A chat UI requires a fourth shape Splunk has not bundled in the SDK examples:**
- Either a custom Splunk view (HTML/JS in `appserver/static/` + a Splunkweb endpoint), or
- A Dashboard Studio v2 dashboard that uses an Input → custom search command bridge, or
- A standalone external React/Vue app that calls Splunk REST + the MCP Server.

None of these patterns has a sample app from Splunk. **Unverified** that the AppInspect process will pass a chat-style HTML view without friction. This is a real risk for the "chat cockpit" framing.

---

## 4. Track 3 — SAIA (NL → SPL) integration surface

Already exhaustively verified in `context/06-splunk-ai-stack/02-saia-ai-assistant-for-spl.md`. Key facts for the architecture decision:

- **No public REST API.** Period. The only programmatic ingress is via the 4 `saia_*` MCP tools, and only when both SAIA (7245) and Splunk MCP Server (7931) are installed on the same instance.
- **Splunk Cloud only.** "Generally available on Splunkbase for use with the Splunk Cloud Platform on AWS." Enterprise can use it "Via Cloud Connected" — meaning federated, not local. There is no on-prem self-hosted SAIA.
- **EULA gate** before enablement.
- **Agent Mode** (v2.0, April 2026) is "Splunk Cloud Platform customers, running version 10.1.x or higher, in a supported AWS region. The FedRAMP version of the assistant does not include the Agent Mode feature."

**Implication:** a hackathon app that wants to call SAIA needs (a) a Cloud tenant, (b) SAIA installed + EULA-accepted, (c) MCP Server installed, (d) MCP token. On a free Enterprise trial, SAIA is unavailable. The build can demonstrate the MCP tool-call shape against `saia_*` only on a Cloud tenant.

---

## 5. Track 4 — Hosted Models access reality

| Model | Access path | Works on free trial? | Invocation syntax | Confidence |
|---|---|---|---|---|
| Foundation-Sec-1.1-8B-Instruct | Splunk Cloud Platform only, via AITK 5.7.0+ Connections tab → "Splunk Hosted Models" option + `\| ai` command | **No** — Cloud paid only | `\| ai prompt="..." provider=<?> model=foundation-sec-...` — exact `provider=` value **not in public docs**, unverified | verified Cloud-only / **unverified syntax** |
| gpt-oss-20b | same | **No** | same — exact `provider=` value **unverified** | verified Cloud-only / **unverified syntax** |
| gpt-oss-120b | same | **No** | same — exact `provider=` value **unverified** | verified Cloud-only / **unverified syntax** |
| CDTSM (Cisco Deep Time Series Model) | AITK 5.7.0 Cloud preview; **AITK 5.7.3 extended preview to on-premises** | **Possibly yes** on Enterprise trial with AITK 5.7.3+ installed (preview/beta, not GA) | SPL: `\| fit CDTSM ...` / `\| apply CDTSM ...` style — exact syntax **not captured in this pass, unverified** | preview status verified / **syntax unverified** |

Citations: Feb 18 2026 launch blog ("generally available for Splunk Cloud Platform customers" — re-fetched live this pass 2026-06-13); `context/06-splunk-ai-stack/04-hosted-models.md`; AITK 5.7.3 release notes per `context/06-splunk-ai-stack/01-ai-toolkit-aitk.md:101-106`.

Live WebFetch 2026-06-13 on `help.splunk.com/.../5.7.4/.../about-the-ai-command`: provider list returned verbatim as "OpenAI, Gemini, Bedrock, Groq, and Ollama" — **Splunk Hosted is not in the public `| ai` docs.** Either the docs are stale (likely, since 5.7.0 release notes already announced Hosted Models option) or the provider name is gated to authenticated Cloud doc views. **Cannot ship a build assuming the syntax without a Cloud tenant to test against.**

### Honest alternatives if access is blocked
If Abu does NOT have a paid Splunk Cloud tenant in time:
- **Option A (Cloud trial):** Splunk Cloud Platform offers a 14-day Cloud trial — **unverified** whether Hosted Models entitlement is included. This is the cleanest test path. Ask the hackathon Slack `#splunk-ai-hackathon` (already flagged in memory `aegis_hosted_models_gap.md`).
- **Option B (Foundation-Sec self-hosted):** the model weights are public at `huggingface.co/fdtn-ai/Foundation-Sec-1.1-8B-Instruct`. Run it under vLLM/Ollama locally, point `OpenAIModel(base_url="http://localhost:11434/v1")` from inside `splunklib.ai`. **Be transparent in the README that this is the open-weights HF version, not Splunk-Cloud-hosted.** This satisfies the spirit of "uses Foundation-Sec" without faking Hosted Models access.
- **Option C (gpt-oss self-hosted):** same pattern — gpt-oss-20b/120b open weights from OpenAI; run under vLLM/Ollama; route via `OpenAIModel(base_url=...)`. Transparent disclosure.
- **Option D (skip Hosted Models entirely):** lean on the three accessible Splunk AI capabilities — Python SDK AI (`splunklib.ai`), Splunk MCP Server (consumer side, with a Splunk Enterprise trial install), and AI Assistant via co-installed SAIA on a Cloud trial if possible. Don't claim Hosted Models in the pitch.

**Do NOT do the v1 mistake** (Ollama-as-Hosted-Models pretending the deployment is native).

---

## 6. Track 5 — Prior projects (verified, cloned)

### Already-shipped hackathon projects
- **`chalithah/splunk-claude-mcp-agent`** — cloned `/tmp/splunk-research/splunk-claude-mcp-agent/`. 222-line `splunk_mcp.py`. Pattern: local FastMCP server bridges Claude Desktop → Splunk Enterprise REST. No Hosted Models. No SAIA. Just: Claude calls local MCP, MCP runs SPL via splunk-sdk. **This wedge is taken.** README explicitly positions itself as the "agentic SOC analyst." Quality: simple, clean, single-file. Bar to beat: real Splunkbase-shaped app + multiple SAIA tools + verifiable Cloud-tier features.
- **`gongahkia/splunk-agentic-ops-hackathon-2026`** — surfaced via WebSearch but not cloned (markdown doc only, no full app). Implies registered teams are public.

### Community MCP starting points (re-stated)
- `splunk/splunk-mcp-server2` — Apache-2.0, FastMCP, has SPL guardrails. Good copy-from base if you go MCP-server-shaped.
- `deslicer/mcp-for-splunk` — Apache-2.0, FastMCP, 20+ tools, full ITSI MCP module at `mcp_itsi/`. **The most production-grade community starting point** if our wedge is "MCP server with X new capability."

### Splunkbase prior winners (recap from existing research)
- DNS Guard AI (Build-a-thon 2025 1st place AI/ML, 128 installs) — pure SPL + MLTK, **zero LLM**. Used `fit DensityFunction`, `fit KMeans k=2`, `anomalydetection`. (`13-architecture-recommendation-v2.md` fact 19.)
- CIMplicity AI (1st place App Dev, 221 installs) — UCC framework, OpenRouter `google/gemini-2.0-flash-001` default, Presidio + spaCy for PII. Shipped synthetic data generator.

Both shipped as REAL Splunkbase apps with proper structure. **Quality bar = "looks like an actual Splunkbase app a SOC team would install," not "demo webapp.**"

---

## 7. The three questions Abu must decide

1. **Do you have, or can you get within 24h, a paid Splunk Cloud Platform tenant (or a verified Cloud trial that includes Hosted Models entitlement)?**
   - YES → the "native AI cockpit" wedge is real; can demo Foundation-Sec + gpt-oss + SAIA + Hosted Models against actual Splunk-managed inference.
   - NO → drop "Splunk Hosted Models" from the headline claim. The build is still strong but it sells on `splunklib.ai` + MCP Server + (self-hosted Foundation-Sec for narrative).

2. **Is the build packaged as a Splunkbase-installable app, OR as an external chat webapp?**
   - Splunkbase app shape (matches DNS Guard / CIMplicity winners; what judges historically reward; AppInspect-friendly) → use `bin/`+`default/`+`metadata/` structure; the three sample apps (`ai_custom_alert_app`, `ai_custom_search_app`, `ai_modinput_app`) are the templates; chat UI lives in `appserver/static/` as custom Splunk view (path NOT exemplified by Splunk, real risk).
   - External webapp → easier UI but loses Splunk-native judging signal; competes with `chalithah/splunk-claude-mcp-agent` shape that's already shipped.

3. **Are you building YOUR OWN MCP server, or ONLY consuming Splunk's official one?**
   - Consumer-only → smaller, faster, but the value-add lives entirely in the agent layer + UI. Hard to differentiate from `chalithah/splunk-claude-mcp-agent`.
   - Plus-your-own-MCP-server (running alongside) → bigger surface, can ship novel tools (`sentinel_*`-style verdicts, ingest-cost analyzers, CDTSM-driven forecasting tools). This is where `deslicer/mcp-for-splunk` is the relevant starting base. **No way to inject tools into Splunk's closed server**, so an alongside MCP is the only extension path.

---

## 8. Recommended architecture

**Facts insufficient for a fully concrete recommendation until Q1 is answered.** But the shape that is robust to all three Q1 answers:

> Build a Splunkbase-shaped app (`bin/` + `default/` + `metadata/` + `appserver/static/`) that:
> - Uses `splunklib.ai.Agent` as the agent core, packaged in `bin/` (proven by the three working sample apps).
> - Ships a custom search command `| <wedge>` (mirroring `agenticreport` from `ai_custom_search_app`) — this is the lowest-risk Splunk-native invocation surface.
> - Ships a custom alert action (mirroring `threat_level_assessment.py`) — judges have rewarded "real Splunk integration shape."
> - Consumes the Splunk MCP Server (app 7931) where available; falls back to direct splunklib REST otherwise. Bearer-token auth, `mcp_tool_execute` capability.
> - Reaches Hosted Models via `| ai provider=<TBD>` IF Q1 is YES; otherwise reaches Foundation-Sec via self-hosted vLLM/Ollama with transparent README disclosure.
> - Optionally ships its own thin FastMCP server alongside, exposing 2–3 novel tools that the official server does not have (the differentiator). Start from `splunk/splunk-mcp-server2`'s guardrails pattern OR `deslicer/mcp-for-splunk`'s loader pattern.
> - Chat UI deferred until UX is the bottleneck — if shipped, lives in `appserver/static/` as a Splunk custom view, NOT as a separate webapp.

**Concrete next step:** answer Q1 to Q3 before any code. Then write the BMad-style spec (sahil-spec-writer) against the chosen branch.

---

## Sources verified in this pass (2026-06-13)

- Hosted Models launch blog (re-fetched): https://www.splunk.com/en_us/blog/artificial-intelligence/splunk-launches-hosted-generative-ai-models.html
- AITK 5.7.4 `| ai` command docs (re-fetched): https://help.splunk.com/en/splunk-cloud-platform/apply-machine-learning/use-ai-toolkit/5.7.4/ai-toolkit-commands-macros-and-visualizations/about-the-ai-command
- Cloned: `splunk/splunk-sdk-python`, `CiscoDevNet/Splunk-MCP-Server-official`, `deslicer/mcp-for-splunk`, `splunk/splunk-mcp-server2`, `chalithah/splunk-claude-mcp-agent` — all under `/tmp/splunk-research/`.
- Existing verified corpus (not re-derived): `workspace/context/06-splunk-ai-stack/{01,02,03,04}.md`, `workspace/context/02-agent-frameworks/06-splunklib-ai-deep-read.md`, `workspace/research/splunk-agentic-ops-2026/{05-prior-patterns,13-architecture-recommendation-v2}.md`.
