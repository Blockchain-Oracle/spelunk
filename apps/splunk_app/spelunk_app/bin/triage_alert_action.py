"""Custom alert action — auto-triage a notable event (Splunk-native entry point).

Registered via default/alert_actions.conf. When a saved search fires, this runs
the agent pipeline over the triggering event(s), classifies + forecasts, and
writes the resulting triage note to the KV Store collection (keyed by
event_id) so the cockpit and dashboards can read it.

INTENT (not yet implemented): read alert results (gzip CSV), run pipeline,
upsert triage note to KV Store. Stub only.
"""

# TODO(phase-5): alert action entry point. Stub only.
