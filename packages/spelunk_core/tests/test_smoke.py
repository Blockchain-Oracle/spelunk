"""Smoke tests for spelunk_core.

Lighter testing posture (per plan §6): a few high-value smoke tests, not a
mock-heavy suite. This file is a placeholder so CI has something to run and the
test layout is established.

INTENT (phase-2): test the pipeline happy path against a generic
OpenAI-compatible model, provider selection from config, and spl.is_read_only.
"""

import spelunk_core


def test_package_imports() -> None:
    assert spelunk_core.__version__ == "0.0.0"
