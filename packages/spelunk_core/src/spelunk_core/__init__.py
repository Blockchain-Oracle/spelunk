"""Spelunk agent core.

Importable, CI-testable Python package holding all agent logic. Runs outside
Splunk (unit tests, local CLI) and is vendored into the Splunk app's ``bin/``
at package time, where thin wrappers import it. Keeping logic here (not in
``bin/``) is what lets it be tested in CI, since ``bin/`` only runs under
Splunk's embedded Python.

Public surface (see individual modules):
    - agent:     builds the splunklib.ai Agent.
    - pipeline:  the SPL -> run -> classify -> forecast -> narrate steps.
    - providers: the LLM provider abstraction (SplunkHosted | SelfHosted | External).
    - events:    the typed step-event wire contract (source of truth for ui-contract).
    - spl:       SPL string helpers.
"""

__version__ = "0.0.0"
