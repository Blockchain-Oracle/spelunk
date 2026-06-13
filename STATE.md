# STATE — where this project is and how it got here

_Last updated: 2026-06-13. This file is the orientation doc for any human or AI agent (including the cloud Ultraplan planner) picking up the repo._

## TL;DR

This repo is a **fresh, clean scaffold** of **Spelunk**, created as ground truth so downstream planners and builders work against the real intended structure rather than inferring it. It is a **pivot** away from a prior project ("SplunkGate") that missed the hackathon brief. The directory structure, config files, docs, and stub modules are in place; **no application logic is implemented yet**.

## The pivot (why "Spelunk", not "SplunkGate")

For ~10 days we built **SplunkGate** — a runtime AI safety-net (guardrail middleware, judges, a custom MCP server, a Cisco AI Defense regex layer, a local-Ollama "explainer"). Reading the Splunk Agentic Ops hackathon brief from first principles revealed two fatal problems:

1. **It used none of the five rewarded Splunk AI surfaces.** The brief rewards: Python SDK AI, Splunk MCP Server, AI Assistant for SPL, AI Toolkit, and Splunk Hosted Models. SplunkGate touched none of them at runtime.
2. **It misread "Agentic Ops."** SplunkGate guarded *generic* agents; the brief wants an agent doing *operational work on Splunk data*. (The local-Ollama-as-"Hosted-Models" claim was self-deception — same model name, wrong product.)

**Spelunk** corrects this: an agentic SOC copilot that operates on Splunk data using Splunk's own AI surfaces.

The old SplunkGate code is **archived, not deleted**, at `../splunk/archive/splunkgate-v1/` in the original workspace — kept only as a reference for proven UI/build patterns (React→webpack→SimpleXML mount, KV-store `transforms.conf`, JSON `props.conf`, the AppInspect harness, the Next.js landing).

## Locked decisions

- **Name:** Spelunk.
- **Track:** Security-primary (Security $3K + Developer Tools $1K + MCP Server stretch $1K; Hosted Models bonus pivotable).
- **Auth:** none custom anywhere — Splunk is the identity provider; gated AI tokens live in `passwords.conf` (setup-time).
- **Website:** static marketing + docs only (no backend, no auth, no hosted demo).
- **Judging:** ship both an installable `.tgz` + demo video AND a hosted Splunk instance with a judge login (Splunk-native login, no custom auth).
- **Gated AI:** a `providers.py` abstraction; real Hosted Models / SAIA wired by config when the Cisco entitlement email is granted; honest self-hosted Foundation-Sec fallback.

## What's in this commit (scaffold only)

- Full monorepo directory structure (`packages/`, `apps/`, `data/`, `docs/`, `tooling/`).
- All config files (`package.json`, `pyproject.toml`, Splunk `*.conf`, webpack/tsconfig, CI).
- `docs/PLAN.md` — the complete system-design + phasing plan.
- `docs/research/` — the two fact-checked grounding reports.
- Stub source files whose docstrings state each module's intent.

## What is NOT done

- No agent logic, no pipeline, no REST handler, no cockpit UI, no synthetic data generator implementation.
- No Splunk install / spike has been run yet (Phase 0 in `docs/PLAN.md`).

## Next step

Per `docs/PLAN.md` §4: **Phase 0 — the day-1 spike** (a throwaway `restmap.conf` hello-world handler on a local Splunk Enterprise trial) to resolve four unverified Splunk unknowns before committing the transport architecture.
