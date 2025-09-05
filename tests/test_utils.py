from __future__ import annotations

import pytest
from datetime import datetime, timezone

from sonec.utils.time import parse_utc, to_rfc3339_z
from sonec.utils.pagination import encode_after_key, decode_after_key


def test_parse_utc_accepts_datetime_and_strings() -> None:
    naive = datetime(2025, 5, 1, 12, 34, 56)
    aware = parse_utc(naive)
    assert aware is not None and aware.tzinfo is not None
    assert aware.tzinfo == timezone.utc

    s = "2025-05-01T12:34:56Z"
    dt = parse_utc(s)
    assert dt is not None and dt.tzinfo == timezone.utc


def test_to_rfc3339_z_outputs_z_suffix() -> None:
    dt = datetime(2025, 5, 1, 12, 34, 56, tzinfo=timezone.utc)
    out = to_rfc3339_z(dt)
    assert out.endswith("Z")
    assert out == "2025-05-01T12:34:56Z"


def test_keyset_encode_decode_roundtrip() -> None:
    dt = datetime(2025, 5, 1, 12, 34, 56, tzinfo=timezone.utc)
    token = encode_after_key(dt, 123)
    k = decode_after_key(token)
    assert k.created_at == dt
    assert k.id == 123


def test_decode_after_key_invalid_token_raises() -> None:
    with pytest.raises(ValueError):
        decode_after_key("not-a-valid-token")

