"""Bluesky provider module.

Implements data fetching from Bluesky's endpoints and returns normalized
batches according to the provider contract. Supports both unauthenticated
access to the public AppView API and authenticated access via app password
(recommended when public endpoints return 403 or are rate-limited).

Authentication
--------------
Two ways to enable authentication:

1) Environment variables:
   - ``BSKY_IDENTIFIER``: your handle or email (e.g., ``alice.bsky.social``)
   - ``BSKY_APP_PASSWORD``: an app password generated in Bluesky settings

2) Programmatic options via ``ProviderOptions.auth``:
   ``{"identifier": "<handle-or-email>", "password": "<app-password>"}``

When authenticated, the provider obtains an access token using
``com.atproto.server.createSession`` and sends ``Authorization: Bearer <token>``
on subsequent requests against ``https://api.bsky.app``.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence
import os

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
from .. import __version__ as _pkg_version


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
        self._default_headers: dict[str, str] = {
            "User-Agent": f"sonec/{_pkg_version} (+https://github.com/rodrigomotta1/sonec)",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self._auth_state: str = "anonymous"
        self._timeout_s: float | int = 10
        self._transport: Any | None = None

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
        self._timeout_s = http_conf.get("timeout_s", 10.0)
        self._transport = http_conf.get("transport")
        headers = dict(self._default_headers)
        headers.update(http_conf.get("headers", {}) or {})

        warnings: list[str] = []
        # Try to authenticate if credentials are present via options or env
        auth_conf = options.auth or {}
        identifier = str(auth_conf.get("identifier") or os.environ.get("BSKY_IDENTIFIER") or "")
        password = str(auth_conf.get("password") or os.environ.get("BSKY_APP_PASSWORD") or os.environ.get("BSKY_PASSWORD") or "")
        if identifier and password:
            try:
                token = self._login(identifier, password, timeout=self._timeout_s, transport=self._transport)
                headers["Authorization"] = f"Bearer {token}"
                self._base_url = "https://api.bsky.app"
                self._auth_state = "authenticated"
            except Exception as exc:
                warnings.append(f"authentication_failed: {exc}")
                self._auth_state = "anonymous"

        self._client = httpx.Client(base_url=self._base_url, timeout=self._timeout_s, transport=self._transport, headers=headers)
        return ProviderSession(
            provider=self.NAME,
            auth_state=self._auth_state,
            capabilities=capabilities,
            rate_limit_policy=None,
            defaults={"page_limit_max": 100},
            warnings=warnings,
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
            if resp.status_code == 403 and "Authorization" not in (self._client.headers or {}):
                raise InvalidQuery(
                    "Public search endpoint returned 403. Provide Bluesky app credentials via env (BSKY_IDENTIFIER, BSKY_APP_PASSWORD) or ProviderOptions.auth to authenticate."
                )
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

    # Internal auth helper ---------------------------------------------------
    def _login(self, identifier: str, password: str, *, timeout: float | int, transport: Any | None) -> str:
        """Authenticate on Bluesky and return an access token.

        Uses ``com.atproto.server.createSession`` on ``https://bsky.social``.
        Requires an app password (generate it in Bluesky settings).
        """
        auth_headers = dict(self._default_headers)
        with httpx.Client(base_url="https://bsky.social", timeout=timeout, transport=transport, headers=auth_headers) as c:
            resp = c.post("/xrpc/com.atproto.server.createSession", json={"identifier": identifier, "password": password})
            if resp.status_code == 401:
                raise InvalidQuery("Invalid Bluesky credentials (use an app password, not your login password).")
            resp.raise_for_status()
            data = resp.json()
            token = data.get("accessJwt")
            if not token:
                raise InvalidQuery("Authentication succeeded but no access token was returned.")
            return str(token)


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
