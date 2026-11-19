"""One way to derive every seed, so any trajectory can be regenerated from its name."""

from __future__ import annotations

import hashlib


def seed_for(*keys) -> int:
    """A 31-bit seed from a tuple of keys (strings or integers). Stable across machines and runs."""
    h = hashlib.sha256("\x1f".join(str(k) for k in keys).encode()).digest()
    return int.from_bytes(h[:4], "big") & 0x7FFFFFFF
