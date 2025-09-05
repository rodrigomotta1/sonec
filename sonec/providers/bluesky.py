"""Bluesky provider module.

Implements data fetching from Bluesky's public endpoints and returns
normalized batches according to the provider contract.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import httpx

from .base import (
    FetchBatch,
    InvalidQuery,
    Metrics,
    Entities,
    Media,
    Post,
    Provider,
    ProviderOptions,
    ProviderSession,
    Author,
)
from ..utils.time import parse_utc


class BlueskyProvider(Provider):
    """Provider implementation skeleton for Bluesky.

    The concrete ``configure`` and ``fetch_since`` implementations will be
    added in a subsequent iteration. This skeleton documents capabilities
    and expected interaction surfaces.
    """

    NAME = "bluesky"

    def __init__(self) -> None:
        self._client: httpx.Client | None = None
        self._base_url: str = "https://public.api.bsky.app"

    def configure(self, options: ProviderOptions) -> ProviderSession:  # pragma: no cover
        """Initialize a Bluesky provider session.

        Parameters
        ----------
        options:
            Provider options with optional authentication and HTTP hints.

        Returns
        -------
        ProviderSession
            Session metadata including declared capabilities.
        """
        capabilities: dict[str, object] = {
            "supports_cursor": True,
            "supports_search_q": True,
            "supports_author_filter": True,
            "supports_lang_filter": True,
            "supports_time_bounds": "inclusive",
            "supports_media": True,
            "max_page_limit": 100,
            "date_granularity": "second",
        }
        http_conf = (options.http or {})
        self._base_url = str(http_conf.get("base_url", self._base_url))
        timeout = http_conf.get("timeout_s", 10.0)
        transport = http_conf.get("transport")
        self._client = httpx.Client(base_url=self._base_url, timeout=timeout, transport=transport)
        return ProviderSession(
            provider=self.NAME,
            auth_state="anonymous",
            capabilities=capabilities,
            rate_limit_policy=None,
            defaults={"page_limit_max": 100},
            warnings=[],
        )

    def fetch_since(self, cursor: str | None, limit: int, filters: Mapping[str, object]) -> FetchBatch:  # pragma: no cover
        """Fetch a normalized batch from Bluesky since the given cursor.

        Parameters
        ----------
        cursor:
            Opaque Bluesky cursor, or ``None`` to start from the beginning.
        limit:
            Maximum desired item count in this batch (provider may reduce).
        filters:
            Filter mapping (e.g., ``{"q": "term"}`` or ``{"author": {"handle": "@user"}}``).

        Returns
        -------
        FetchBatch
            Normalized items and cursor information.
        """
        if self._client is None:
            raise RuntimeError("Provider not configured. Call configure() first.")

        # Determine mode: search (q) or author feed (handle/external_id)
        q = filters.get("q") if isinstance(filters, Mapping) else None
        author = filters.get("author") if isinstance(filters, Mapping) else None

        page_limit = min(int(limit or 10), 100)
        ignored: list[str] = []
        for k in ("since_utc", "until_utc", "lang", "domain", "tags"):
            if k in filters:
                ignored.append(k)

        if q:
            # searchPosts endpoint
            params = {"q": str(q), "limit": page_limit}
            if cursor:
                params["cursor"] = cursor
            resp = self._client.get("/xrpc/app.bsky.feed.searchPosts", params=params)
            resp.raise_for_status()
            payload = resp.json()
            posts = payload.get("posts", [])
            next_cursor = payload.get("cursor")
            items = self._normalize_post_list(posts, source=str(q))
            return FetchBatch(
                items=items,
                next_cursor=next_cursor,
                reached_until=False,
                ignored_filters=ignored,
                stats={"count": len(items)},
                rate_limit=None,
                warnings=[],
            )

        # Author feed endpoint requires a handle or external_id
        actor: str | None = None
        if isinstance(author, Mapping):
            handle = author.get("handle")
            ext_id = author.get("external_id")
            if isinstance(handle, str) and handle:
                actor = handle[1:] if handle.startswith("@") else handle
            elif isinstance(ext_id, str):
                actor = ext_id

        if actor:
            params = {"actor": actor, "limit": page_limit}
            if cursor:
                params["cursor"] = cursor
            resp = self._client.get("/xrpc/app.bsky.feed.getAuthorFeed", params=params)
            resp.raise_for_status()
            payload = resp.json()
            feed = payload.get("feed", [])
            posts = [entry.get("post") for entry in feed if isinstance(entry, Mapping) and entry.get("post")]
            next_cursor = payload.get("cursor")
            source = f"@{actor}" if not actor.startswith("did:") and not actor.startswith("@") else actor
            items = self._normalize_post_list(posts, source=source)
            return FetchBatch(
                items=items,
                next_cursor=next_cursor,
                reached_until=False,
                ignored_filters=ignored,
                stats={"count": len(items)},
                rate_limit=None,
                warnings=[],
            )

        raise InvalidQuery("Bluesky requires either 'q' or author {'handle'|'external_id'} filter")

    # Internal helpers -----------------------------------------------------

    def _normalize_post_list(self, posts: Sequence[Mapping[str, Any]], *, source: str | None) -> list[Post]:
        items: list[Post] = []
        now = datetime_now_utc()
        for p in posts:
            uri = str(p.get("uri"))
            author = p.get("author", {})
            record = p.get("record", {})
            text = str(record.get("text", ""))
            created_at = parse_utc(record.get("createdAt")) or now

            author_obj = Author(
                external_id=str(author.get("did", "")),
                handle=f"@{author.get('handle')}" if author.get("handle") else None,
                display_name=str(author.get("displayName")) if author.get("displayName") else None,
                avatar_url=None,
                metadata=None,
            )

            metrics = Metrics(
                like_count=_as_int(p.get("likeCount")),
                reply_count=_as_int(p.get("replyCount")),
                repost_count=_as_int(p.get("repostCount")),
            )

            entities = Entities(hashtags=[], mentions=[], links=[], media=[])

            items.append(
                Post(
                    provider=self.NAME,
                    external_id=uri,
                    created_at=created_at,
                    collected_at=now,
                    author=author_obj,
                    text=text,
                    lang=p.get("lang") if isinstance(p.get("lang"), str) else None,
                    metrics=metrics,
                    entities=entities,
                    visibility="public",
                    in_reply_to=None,
                    repost_of=None,
                    quote_of=None,
                    source=source,
                    raw=None,
                )
            )
        return items


def _as_int(v: Any) -> int | None:
    try:
        if v is None:
            return None
        return int(v)
    except Exception:
        return None


def datetime_now_utc() -> datetime:
    from datetime import datetime, timezone

    return datetime.now(tz=timezone.utc)
