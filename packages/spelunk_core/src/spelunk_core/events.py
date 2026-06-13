"""The step-event wire contract — SOURCE OF TRUTH for the cockpit's generative UI.

Every step of the agent pipeline emits one of these typed events. The cockpit
maps ``event.type`` -> a React component (the generative-UI registry). This
module is hand-synced to ``packages/ui-contract/src/events.ts`` — keep them
identical (codegen is intentionally avoided for now).

Event types (one React component each):
    - "spl":            generated SPL  -> <SplBlock onRun>
    - "results":        search results -> <ResultsTable>
    - "classification": MITRE mapping  -> <MitreCard>
    - "forecast":       CDTSM forecast -> <ForecastChart>
    - "narrative":      LLM summary    -> <Narrative>
    - "error":          failure        -> <ErrorBanner>

INTENT (not yet implemented): define a discriminated union (TypedDict or
dataclasses + Literal "type" tags) plus a small ``to_dict`` so the REST handler
can serialize events to the cockpit. No behavior beyond shaping the contract.
"""

from __future__ import annotations

# TODO(phase-2): define StepEvent union + serialization. Stub only.
