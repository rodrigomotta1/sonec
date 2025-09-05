from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from sonec import api


def _post(idx: int, handle: str = "alice.bsky.social") -> dict[str, Any]:
    return {
        "post": {
            "uri": f"at://{handle}/post/{idx}",
            "cid": f"cid-{idx}",
            "author": {"did": f"did:plc:{handle}", "handle": handle, "displayName": handle.split(".")[0].title()},
            "record": {"$type": "app.bsky.feed.post", "text": f"hello {idx}", "createdAt": "2025-05-01T12:00:00Z"},
            "likeCount": idx,
            "repostCount": 0,
            "replyCount": 0,
        }
    }


def test_collect_author_feed_paginates_and_persists() -> None:
    api.configure()
    from sonec.core.models import Post, Source, Cursor, FetchJob

    # Mock two pages: first with 2 posts + cursor, second with 1 post and no cursor
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("getAuthorFeed"):
            params = dict(request.url.params)
            assert params.get("actor") == "alice.bsky.social"
            cursor = params.get("cursor")
            if cursor is None:
                body = {"feed": [_post(1), _post(2)], "cursor": "next-1"}
            else:
                body = {"feed": [_post(3)], "cursor": None}
            return httpx.Response(200, json=body)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    report = api.collect(
        provider="bluesky",
        source="@alice.bsky.social",
        page_limit=2,
        limit=3,
        extras={"http": {"transport": transport, "base_url": "https://unit.test"}},
    )

    assert report["provider"] == "bluesky"
    assert report["source"] == "@alice.bsky.social"
    assert report["inserted"] == 3
    assert report["conflicts"] == 0
    # The last non-None cursor encountered should be preserved
    assert report["last_cursor"] == "next-1"

    # Validate DB state
    assert Post.objects.filter(provider_id="bluesky").count() == 3
    src = Source.objects.get(provider_id="bluesky", descriptor="@alice.bsky.social")
    cur = Cursor.objects.get(provider_id="bluesky", source=src)
    assert cur.position.get("cursor") == "next-1"

    job = FetchJob.objects.order_by("-started_at").first()
    assert job is not None and job.status in ("succeeded", "completed")
    assert job.stats.get("inserted") == 3


def test_collect_is_idempotent_counts_conflicts() -> None:
    api.configure()
    from sonec.core.models import Post, Cursor, FetchJob, Source

    # Ensure isolation from previous tests
    Post.objects.all().delete()
    Cursor.objects.all().delete()
    FetchJob.objects.all().delete()
    Source.objects.filter(descriptor="@alice.bsky.social").delete()

    # Single page returning same two posts always
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("getAuthorFeed"):
            body = {"feed": [_post(1), _post(2)], "cursor": "c1"}
            return httpx.Response(200, json=body)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)

    # First run inserts 2
    report1 = api.collect(
        provider="bluesky",
        source="@alice.bsky.social",
        page_limit=10,
        limit=2,
        extras={"http": {"transport": transport, "base_url": "https://unit.test"}},
    )
    assert report1["inserted"] == 2 and report1["conflicts"] == 0

    # Second run hits dedup constraint -> 0 inserted, 2 conflicts
    report2 = api.collect(
        provider="bluesky",
        source="@alice.bsky.social",
        page_limit=10,
        limit=2,
        extras={"http": {"transport": transport, "base_url": "https://unit.test"}},
    )
    assert report2["inserted"] == 0 and report2["conflicts"] == 2
