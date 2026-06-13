"""The agent pipeline: NL question -> SPL -> run -> classify -> forecast -> narrate.

Decomposed into DISCRETE SHORT STEPS on purpose: each step is a separate short
agent invocation that emits one events.StepEvent, so (a) the cockpit can render
progressively, and (b) no single request approaches the splunkd Web-proxy
timeout. The same step sequence backs both the polling transport and a future
streaming upgrade.

Step order (each yields one event):
    1. nl2spl    -> "spl"            (SAIA saia_generate_spl, or LLM)
    2. run       -> "results"        (MCP splunk_run_query / SplunkJS)
    3. classify  -> "classification" (Foundation-Sec -> MITRE technique)
    4. forecast  -> "forecast"       (CDTSM escalation / volume)
    5. narrate   -> "narrative"      (gpt-oss analyst summary)

INTENT (not yet implemented): a generator ``run_pipeline(question, ctx)`` that
yields events; pure orchestration over agent.py + tools. No logic yet.
"""

from __future__ import annotations

# TODO(phase-2): run_pipeline(...) generator yielding StepEvents. Stub only.
