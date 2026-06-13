"""Builds the splunklib.ai Agent (the rewarded Python SDK AI surface).

Thin constructor that assembles a ``splunklib.ai.Agent`` from a chosen provider
(see providers.py) and the tool set (see the app's bin/tools.py wiring): SPL
generation, search execution, threat classification, forecasting. The agent is
driven step-by-step by pipeline.py so no single invocation holds the splunkd
connection near its timeout.

INTENT (not yet implemented): ``build_agent(provider, service, tools)`` ->
configured Agent; ``AgentLimits`` tuned for short per-step invokes. No logic yet.
"""

from __future__ import annotations

# TODO(phase-2): build_agent(...) wiring splunklib.ai.Agent. Stub only.
