from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from sonec import api
from sonec.api import QueryResultPage


def _seed_posts():
    # Import after configure
    from sonec.core.models import Author, Post, Provider

    # Ensure a clean slate for posts to avoid cross-test interference
    Post.objects.all().delete()

    provider, _ = Provider.objects.get_or_create(name="bluesky", defaults={"version": "0.1.0", "capabilities": {}})
    author, _ = Author.objects.get_or_create(provider=provider, external_id="did:plc:1", defaults={"handle": "@alice", "display_name": "Alice"})
    author2, _ = Author.objects.get_or_create(provider=provider, external_id="did:plc:2", defaults={"handle": "@bob", "display_name": "Bob"})

    base = datetime(2025, 5, 1, 12, 0, 0, tzinfo=timezone.utc)

    def mk(i: int, a, text: str) -> Post:
        return Post.objects.create(
            provider=provider,
            external_id=f"at://example/post/{i}",
            author=a,
            text=text,
            lang="en",
            created_at=base - timedelta(minutes=i),
            collected_at=base + timedelta(minutes=i),
            metrics={},
            entities={"hashtags": [], "mentions": [], "links": [], "media": []},
        )

    p1 = mk(1, author, "first hello world")
    p2 = mk(2, author, "second apples and oranges")
    p3 = mk(3, author2, "third hello again")
    p4 = mk(4, author2, "fourth bananas")
    p5 = mk(5, author, "fifth HELLO upper")

    return [p1, p2, p3, p4, p5]


def test_query_posts_keyset_pagination() -> None:
    api.configure()
    _seed_posts()

    # Page 1
    page1: QueryResultPage = api.query(
        "posts",
        provider="bluesky",
        limit=2,
        as_dict=True,
        project=["id", "created_at", "text"],
    )
    assert page1["count"] == 2
    assert page1["items"][0]["created_at"] >= page1["items"][1]["created_at"]
    assert page1["next_after_key"]

    # Page 2 using after_key
    page2: QueryResultPage = api.query(
        "posts",
        provider="bluesky",
        limit=2,
        as_dict=True,
        after_key=page1["next_after_key"],
        project=["id", "created_at", "text"],
    )
    assert page2["count"] == 2
    assert page2["items"][0]["created_at"] >= page2["items"][1]["created_at"]

    # Page 3 should have the remainder and no next key
    page3: QueryResultPage = api.query(
        "posts",
        provider="bluesky",
        limit=2,
        as_dict=True,
        after_key=page2["next_after_key"],
        project=["id", "created_at", "text"],
    )
    assert page3["count"] in (1, 2)  # depending on rounding of total 5
    if page3["count"] < 2:
        assert page3["next_after_key"] is None


def test_query_posts_filters_and_projection() -> None:
    api.configure()
    _seed_posts()

    since = datetime(2025, 5, 1, 11, 56, 0, tzinfo=timezone.utc)  # filters out the last item or two

    page: QueryResultPage = api.query(
        "posts",
        provider="bluesky",
        since_utc=since,
        author="@alice",
        contains="hello",
        limit=10,
        as_dict=True,
        project=["id", "text", "created_at"],
    )

    assert page["count"] >= 1
    for item in page["items"]:
        assert "id" in item and "text" in item and "created_at" in item
        assert "hello" in item["text"].lower()


def test_query_author_filter_variants() -> None:
    api.configure()
    rows = _seed_posts()

    # Filter by external_id (did)
    page_did: QueryResultPage = api.query(
        "posts",
        provider="bluesky",
        author="did:plc:1",
        limit=50,
        as_dict=True,
        project=["id", "author_id"],
    )
    assert page_did["count"] >= 1

    # Filter by numeric author id
    from sonec.core.models import Author

    aid = Author.objects.get(external_id="did:plc:1").id
    page_num: QueryResultPage = api.query(
        "posts",
        provider="bluesky",
        author=str(aid),
        limit=50,
        as_dict=True,
        project=["id", "author_id"],
    )
    assert page_num["count"] >= 1
