"""Time parsing and normalization utilities.

This module provides helpers to parse RFC 3339/ISO 8601 timestamps and ensure
timezone-aware UTC datetimes throughout the system.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def parse_utc(value: datetime | str | None) -> datetime | None:
    """Parse a datetime or RFC 3339 string into an aware UTC datetime.

    Parameters
    ----------
    value:
        A :class:`datetime.datetime` (aware or naive) or an ISO/RFC 3339 string.

    Returns
    -------
    datetime | None
        A timezone-aware UTC datetime, or ``None`` when ``value`` is ``None``.
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            # Assume naive datetimes are UTC
            return value.replace(tzinfo=timezone.utc)
        
        return value.astimezone(timezone.utc)

    s = str(value).strip()

    # Normalize trailing Z to +00:00 for fromisoformat
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)

    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Invalid datetime format: {value!r}") from exc

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    else:
        dt = dt.astimezone(timezone.utc)

    return dt


def to_rfc3339_z(dt: datetime) -> str:
    """Format a datetime as RFC 3339 with Z suffix.

    Parameters
    ----------
    dt:
        A timezone-aware datetime.

    Returns
    -------
    str
        RFC 3339 string with ``Z`` suffix.
    """

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    else:
        dt = dt.astimezone(timezone.utc)
        
    # Use timespec=seconds to avoid microseconds noise in tokens
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")

