from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx
import pytest

from sonec.providers.bluesky import BlueskyProvider
from sonec.providers.base import ProviderOptions, InvalidQuery


def _post(
    idx: int,
    did: str = "did:plc:alice",
    handle: str = "alice.bsky.social",
    display: str = "Alice",
    text: str = "hello world",
    created: str = "2025-05-01T12:00:00Z",
    likes: int = 1,
    reposts: int = 0,
    replies: int = 0,
) -> dict[str, Any]:
    uri = f"at://{handle}/post/{idx}"
    return {
        "uri": uri,
        "cid": f"cid-{idx}",
        "author": {"did": did, "handle": handle, "displayName": display},
        "record": {"$type": "app.bsky.feed.post", "text": text, "createdAt": created},
        "likeCount": likes,
        "repostCount": reposts,
        "replyCount": replies,
    }


def test_search_posts_fetch_batch() -> None:
    # Mock transport routing the search endpoint
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/xrpc/app.bsky.feed.searchPosts"
        params = dict(request.url.params)
        q = params.get("q")
        assert q == "hello"
        limit = int(params.get("limit", "10"))
        cursor = params.get("cursor")
        posts = [_post(1), _post(2)]
        body: dict[str, Any] = {"posts": posts[:limit]}
        if cursor is None:
            body["cursor"] = "next-1"
        return httpx.Response(200, json=body)

    transport = httpx.MockTransport(handler)
    p = BlueskyProvider()
    session = p.configure(ProviderOptions(http={"transport": transport, "base_url": "https://unit.test"}))
    assert session.provider == "bluesky"

    batch = p.fetch_since(None, limit=2, filters={"q": "hello"})
    assert batch.next_cursor == "next-1"
    assert batch.reached_until is False
    assert batch.stats.get("count") == 2
    assert len(batch.items) == 2

    it = batch.items[0]
    assert it.provider == "bluesky"
    assert it.external_id.startswith("at://")
    assert it.author.external_id.startswith("did:")
    assert it.text
    assert it.created_at.tzinfo == timezone.utc


def test_author_feed_fetch_batch() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/xrpc/app.bsky.feed.getAuthorFeed"
        params = dict(request.url.params)
        assert params.get("actor") == "alice.bsky.social"
        body = {"feed": [{"post": _post(10)}], "cursor": None}
        return httpx.Response(200, json=body)

    p = BlueskyProvider()
    transport = httpx.MockTransport(handler)
    p.configure(ProviderOptions(http={"transport": transport, "base_url": "https://unit.test"}))

    batch = p.fetch_since(None, limit=5, filters={"author": {"handle": "@alice.bsky.social"}})
    assert batch.next_cursor is None
    assert batch.stats.get("count") == 1
    assert len(batch.items) == 1
    assert batch.items[0].author.handle == "@alice.bsky.social"


def test_invalid_filters_raise() -> None:
    p = BlueskyProvider()
    p.configure(ProviderOptions(http={"transport": httpx.MockTransport(lambda r: httpx.Response(500))}))
    with pytest.raises(InvalidQuery):
        p.fetch_since(None, limit=10, filters={})

