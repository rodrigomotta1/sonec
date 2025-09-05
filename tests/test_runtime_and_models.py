from __future__ import annotations

from datetime import datetime, timezone

import pytest

from sonec import api


def test_configure_in_memory_sqlite_creates_schema() -> None:
    info = api.configure()  # default: in-memory
    assert info.initialized is True
    assert info.backend == "sqlite"
    assert isinstance(info.database, str)


def test_model_crud_and_uniqueness_constraints() -> None:
    api.configure()

    # Import models after Django is configured to avoid ImproperlyConfigured during collection
    from sonec.core.models import Author, Media, Post, Provider, Source

    provider = Provider.objects.create(name="bluesky", version="0.1.0", capabilities={"supports_cursor": True})
    source = Source.objects.create(provider=provider, descriptor="@example", label="Example")
    author = Author.objects.create(
        provider=provider,
        external_id="did:plc:123",
        handle="@example",
        display_name="Example",
    )

    created_at = datetime(2025, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
    collected_at = datetime.now(tz=timezone.utc)

    post = Post.objects.create(
        provider=provider,
        external_id="at://example/post/1",
        author=author,
        text="Hello world",
        lang="en",
        created_at=created_at,
        collected_at=collected_at,
        metrics={"like_count": 1},
        entities={"hashtags": ["test"], "mentions": [], "links": [], "media": []},
    )

    Media.objects.create(post=post, kind="image", url="https://example.com/image.jpg", metadata={})

    # Attempt to insert duplicate post for same (provider, external_id)
    with pytest.raises(Exception):
        Post.objects.create(
            provider=provider,
            external_id="at://example/post/1",
            author=author,
            text="Duplicate",
            created_at=created_at,
            collected_at=collected_at,
        )

    # Basic retrieval and ordering check
    rows = list(Post.objects.filter(provider=provider).order_by("-created_at", "-id")[:10])
    assert rows and rows[0].id == post.id


def test_api_scaffolds_raise_not_implemented() -> None:
    api.configure()

    with pytest.raises(NotImplementedError):
        api.collect(provider="bluesky", source="@example")

    with pytest.raises(NotImplementedError):
        api.query("posts", provider="bluesky", limit=1)
