"""Synthetic security-event generator for sourcetype ``spelunk:auth``.

Produces a deterministic JSON dataset a SOC analyst would query: logins, failed
auth, privilege escalation, file access — with embedded attack scenarios
(e.g. brute-force from new geos -> T1110, valid-account misuse -> T1078) so the
demo has real signal. Output seeds the app's bundled monitor input and the
hosted judging instance.

Event fields (plan §1b): _time, user, src_ip, dest_host, action, auth_method,
event_type, failure_count, geo_country, user_agent, mitre_technique_id,
mitre_tactic_id, risk_score, event_id.

INTENT (phase-3): stdlib-only, seeded RNG, --out / --count flags, writes
newline-delimited JSON. Adapt from the archived Synthetic-Data/ generators.
Stub only.
"""

from __future__ import annotations

# TODO(phase-3): deterministic spelunk:auth generator. Stub only.

if __name__ == "__main__":
    raise SystemExit("not implemented yet (scaffold)")
