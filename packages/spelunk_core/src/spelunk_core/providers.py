"""LLM provider abstraction — the gated-AI plug-in point.

Lets the pipeline run end-to-end today on a generic OpenAI-compatible model,
and swap to Splunk Hosted Models / SAIA by CONFIG ONLY (no code change) when
the Cisco entitlement is granted. This is the single seam that makes the
"gated surfaces" strategy work without rework.

Implementations (selected via the app's spelunk.conf):
    - SplunkHostedProvider: routes via `| ai provider=splunk_hosted model=...`
      (Foundation-Sec / gpt-oss) and `| apply CDTSM`. Splunk-Cloud-entitled.
    - SelfHostedProvider:   Foundation-Sec / gpt-oss open weights under
      Ollama/vLLM via OpenAIModel(base_url=...). The HONEST fallback —
      README states plainly this is open-weights, NOT Splunk-hosted.
    - ExternalProvider:     OpenAI / Anthropic, for local dev convenience.

INTENT (not yet implemented): an ``LLMProvider`` Protocol with ``complete()``
and ``classify()``; a ``provider_from_config(conf)`` factory. No network calls
or model wiring yet.
"""

from __future__ import annotations

# TODO(phase-2): LLMProvider Protocol + 3 implementations + factory. Stub only.
