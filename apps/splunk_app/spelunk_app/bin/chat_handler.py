"""Custom REST handler — the cockpit <-> agent transport.

Registered via default/restmap.conf as a PersistentServerConnectionApplication
running inside splunkd. The cockpit (React in Splunk Web) calls this same-origin
at /splunkd/__raw/services/spelunk/chat, so it inherits the Splunk session
cookie + CSRF — no custom auth. Gated AI tokens are read server-side from
passwords.conf.

Transport (plan §1e): POLLING FIRST. POST /chat/start -> job_id; the cockpit
then GETs /chat/step?job_id&cursor for each pipeline step, stashed in a KV Store
collection. Streaming (SSE/chunked) is a later upgrade IF the Phase-0 spike
shows bytes flush through the splunkd Web proxy.

This file is a THIN WRAPPER: it adapts Splunk's request/response to
spelunk_core.pipeline (vendored at package time) and serializes events.

INTENT (not yet implemented): the handler class + start/step routing. Stub only.
"""

# TODO(phase-4): PersistentServerConnectionApplication subclass. Stub only.
