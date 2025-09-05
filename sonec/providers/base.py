"""Provider base interfaces and typed structures.

This module defines contracts, canonical structures and exceptions used by
provider implementations. Providers are responsible for retrieving posts
from a given social network and returning batches of normalized posts.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping, MutableMapping, Sequence


# Exceptions -----------------------------------------------------------------


class ProviderError(Exception):
    """Base exception for provider-related errors."""


class RateLimited(ProviderError):
    """Signals rate-limit conditions with an optional retry hint."""

    def __init__(self, message: str, *, retry_after_s: int | None = None, reset_at: datetime | None = None, request_id: str | None = None) -> None:
        super().__init__(message)
        self.retry_after_s = retry_after_s
        self.reset_at = reset_at
        self.request_id = request_id


class TemporaryNetworkError(ProviderError):
    """Transient network failures such as timeouts, DNS errors, or 5xx."""

    def __init__(self, message: str, *, retry_after_s: int | None = None) -> None:
        super().__init__(message)
        self.retry_after_s = retry_after_s


class AuthError(ProviderError):
    """Authentication or authorization failure."""


class InvalidQuery(ProviderError):
    """Invalid or unsupported query parameters were provided."""


class ProviderUnavailable(ProviderError):
    """Provider is unavailable due to maintenance or outages."""


# Canonical structures --------------------------------------------------------


@dataclass(slots=True)
class Author:
    external_id: str
    handle: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(slots=True)
class Media:
    kind: str
    url: str
    mime_type: str | None = None
    width: int | None = None
    height: int | None = None
    duration_ms: int | None = None
    thumbnail_url: str | None = None
    alt_text: str | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(slots=True)
class Entities:
    hashtags: Sequence[str]
    mentions: Sequence[Mapping[str, str | None]]
    links: Sequence[Mapping[str, Any]]
    media: Sequence[Media]


@dataclass(slots=True)
class Metrics:
    like_count: int | None = None
    reply_count: int | None = None
    repost_count: int | None = None
    quote_count: int | None = None
    view_count: int | None = None
    bookmark_count: int | None = None
    score: float | None = None
    extra: Mapping[str, Any] | None = None


@dataclass(slots=True)
class Post:
    provider: str
    external_id: str
    created_at: datetime
    collected_at: datetime
    author: Author
    text: str
    lang: str | None = None
    metrics: Metrics | None = None
    entities: Entities | None = None
    visibility: str | None = None
    in_reply_to: Mapping[str, Any] | None = None
    repost_of: Mapping[str, Any] | None = None
    quote_of: Mapping[str, Any] | None = None
    source: str | None = None
    raw: Mapping[str, Any] | None = None


@dataclass(slots=True)
class ProviderOptions:
    auth: Mapping[str, Any] | None = None
    http: Mapping[str, Any] | None = None
    hints: Mapping[str, Any] | None = None
    scope_defaults: Mapping[str, Any] | None = None


@dataclass(slots=True)
class ProviderSession:
    provider: str
    auth_state: str
    capabilities: Mapping[str, Any]
    rate_limit_policy: Mapping[str, Any] | None
    defaults: Mapping[str, Any] | None
    warnings: Sequence[str]


@dataclass(slots=True)
class FetchBatch:
    items: Sequence[Post]
    next_cursor: str | None
    reached_until: bool
    ignored_filters: Sequence[str]
    stats: Mapping[str, Any]
    rate_limit: Mapping[str, Any] | None
    warnings: Sequence[str]


class Provider:
    """Abstract base class for providers.

    Concrete providers should implement the ``configure`` and ``fetch_since``
    methods to initialize session options and retrieve normalized post batches.
    """

    def configure(self, options: ProviderOptions) -> ProviderSession:  # pragma: no cover - interface only
        raise NotImplementedError

    def fetch_since(self, cursor: str | None, limit: int, filters: Mapping[str, Any]) -> FetchBatch:  # pragma: no cover - interface only
        raise NotImplementedError

