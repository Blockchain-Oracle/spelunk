# Spelunk

**An agentic SOC copilot, packaged as a native Splunk app with a generative-UI chat cockpit.**

A SOC analyst opens Spelunk inside Splunk Web and asks security questions in natural language. An agent turns the question into SPL, runs it on Splunk data, classifies findings against MITRE ATT&CK, forecasts escalation, and writes an analyst-ready summary — rendering each step as a typed, interactive React component in the chat stream.

Spelunk is built on Splunk's own AI surfaces: **Python SDK AI (`splunklib.ai`)**, the **Splunk MCP Server**, **AI Assistant for SPL (SAIA)**, and **Splunk Hosted Models** (Foundation-Sec, gpt-oss, CDTSM).

> Submission for the Splunk Agentic Ops hackathon. Track: Security (+ Developer Tools / MCP Server bonuses).

## Why this exists

Splunk SOC analysts drown in alerts — thousands a day, minutes each. Spelunk does the painful first-pass investigation work *on* Splunk data: gather context, classify the threat, predict whether it escalates, and draft the triage note — so the analyst decides instead of digs.

## Monorepo layout

```
packages/
  spelunk_core/      Importable, CI-testable Python agent (splunklib.ai). Vendored into the app at package time.
  ui-contract/       Shared TypeScript step-event union — the generative-UI registry key.
apps/
  splunk_app/        The installable Splunk app (.tgz). Thin bin/ wrappers + default/ confs + appserver/static.
  cockpit/           React SPA → webpack → the app's static/. The generative-UI chat cockpit.
  landing/           Static marketing + docs site (Next.js).
data/                Synthetic security-event generator (sourcetype spelunk:auth).
docs/                PLAN.md (full implementation plan) + research/ (grounding reports).
tooling/             SLIM packaging + CI helpers.
```

## Status

Early scaffold. See `docs/PLAN.md` for the full system design (auth model, data model, end-to-end user flow, phasing) and `STATE.md` for the pivot history. Nothing in the pipeline/cockpit/agent is implemented yet — this commit establishes the structure as ground truth.

## Rewarded Splunk AI surface coverage

| Surface | Use in Spelunk |
|---|---|
| Python SDK AI (`splunklib.ai`) | Agent core (`packages/spelunk_core`), run from the app's `bin/`. |
| Splunk MCP Server | Agent reads Splunk data via `splunk_run_query` etc. |
| AI Assistant (SAIA) | `saia_generate_spl` for NL→SPL. |
| Hosted Models (Foundation-Sec / gpt-oss) | Threat classification + narrative, via a config-driven provider abstraction. |
| Hosted Models (CDTSM) | Escalation / alert-volume forecasting (`\| apply CDTSM`). |

## Constraints

- Every source file ≤ 400 LOC.
- No custom authentication anywhere — Splunk is the identity provider; gated AI tokens are setup-time config.
- Gated models (Hosted Models / SAIA) plug in by config when entitlement is granted; honest self-hosted fallback, never claimed as Splunk-hosted.

## License

See `LICENSE`.
