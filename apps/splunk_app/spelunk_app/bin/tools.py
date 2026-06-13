"""Agent tool wiring (thin) — the tools the splunklib.ai Agent can call.

Defines the callable tools the pipeline hands to the agent, each a thin adapter
over a real service:
    - run_spl:    execute SPL (Splunk MCP splunk_run_query, or splunklib search).
    - nl2spl:     NL -> SPL via SAIA saia_generate_spl (when entitled).
    - classify:   threat -> MITRE technique via Foundation-Sec (provider).
    - forecast:   time series -> escalation forecast via CDTSM.

Logic lives in spelunk_core; this file only binds it to the live Splunk
``service`` available inside bin/.

INTENT (not yet implemented): tool callables + registration. Stub only.
"""

# TODO(phase-2/6): tool adapters over MCP / splunklib / providers. Stub only.
