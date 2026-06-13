"""SPL string helpers.

Small, pure utilities for building and sanitizing SPL — index/sourcetype
scoping (``index=spelunk_security sourcetype=spelunk:auth``), safe interpolation
of user-supplied values, and a guard that the generated SPL is read-only (no
``| delete``, ``| collect`` into arbitrary indexes, etc.) before it runs.

INTENT (not yet implemented): ``scope(query)``, ``is_read_only(query)``,
``quote(value)``. Pure functions, easy to unit test. No logic yet.
"""

from __future__ import annotations

# TODO(phase-2): SPL helpers. Stub only.
