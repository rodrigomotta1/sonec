from __future__ import annotations

from typing import Any

from sonec import api


def test_status_snapshot_with_filters() -> None:
    api.configure()
    from django.utils import timezone
    from sonec.core.models import Provider, Source, Cursor, FetchJob

    # Clean existing state for deterministic assertions
    Cursor.objects.all().delete()
    FetchJob.objects.all().delete()

    bluesky, _ = Provider.objects.get_or_create(name="bluesky", defaults={"version": "0.1.0", "capabilities": {}})
    other, _ = Provider.objects.get_or_create(name="other", defaults={"version": "0.0", "capabilities": {}})

    src_a, _ = Source.objects.get_or_create(provider=bluesky, descriptor="status-alice", defaults={"label": "alice"})
    src_b, _ = Source.objects.get_or_create(provider=other, descriptor="status-bob", defaults={"label": "bob"})

    # Cursors
    c1, _ = Cursor.objects.get_or_create(provider=bluesky, source=src_a, defaults={"position": {"cursor": "c1"}})
    c1.position = {"cursor": "c1"}
    c1.save(update_fields=["position", "updated_at"])

    c2, _ = Cursor.objects.get_or_create(provider=other, source=src_b, defaults={"position": {"cursor": "c2"}})
    c2.position = {"cursor": "c2"}
    c2.save(update_fields=["position", "updated_at"])

    # Jobs (ensure ordering by started_at desc is visible)
    t0 = timezone.now()
    FetchJob.objects.create(provider=bluesky, source=src_a, started_at=t0, finished_at=t0, status="succeeded", stats={"inserted": 1})
    FetchJob.objects.create(provider=bluesky, source=src_a, started_at=t0.replace(microsecond=1), finished_at=t0, status="succeeded", stats={"inserted": 2})
    FetchJob.objects.create(provider=other, source=src_b, started_at=t0, finished_at=t0, status="succeeded", stats={"inserted": 3})

    snap = api.status(provider="bluesky", source="status-alice", limit_jobs=5)
    assert "cursors" in snap and "jobs" in snap
    assert len(snap["cursors"]) == 1
    assert snap["cursors"][0]["provider"] == "bluesky"
    assert snap["cursors"][0]["source"] == "status-alice"
    assert snap["cursors"][0]["cursor"] == "c1"

    assert len(snap["jobs"]) >= 2
    assert all(j["provider"] == "bluesky" and j["source"] == "status-alice" for j in snap["jobs"])  # type: ignore[index]

    # Without filters, both providers appear
    snap_all = api.status(limit_jobs=10)
    provs = {c["provider"] for c in snap_all["cursors"]}
    assert {"bluesky", "other"}.issubset(provs)

