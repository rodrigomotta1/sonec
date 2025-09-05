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
    """Signals rate-limit conditions with an optional retry hint.

    Parameters
    ----------
    message:
        Human-readable description of the rate-limit condition.
    retry_after_s:
        Optional number of seconds to wait before retrying.
    reset_at:
        Optional UTC timestamp indicating when the quota resets.
    request_id:
        Optional provider request identifier associated with the response.
    """

    def __init__(self, message: str, *, retry_after_s: int | None = None, reset_at: datetime | None = None, request_id: str | None = None) -> None:
        super().__init__(message)
        self.retry_after_s = retry_after_s
        self.reset_at = reset_at
        self.request_id = request_id


class TemporaryNetworkError(ProviderError):
    """Transient network failures such as timeouts, DNS errors, or 5xx.

    Parameters
    ----------
    message:
        Human-readable description of the failure.
    retry_after_s:
        Optional number of seconds to wait before retrying.
    """

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
    """Canonical author representation.

    Attributes
    ----------
    external_id:
        Stable provider-specific author identifier (e.g., DID on Bluesky).
    handle:
        Optional human-readable handle (e.g., ``@alice``).
    display_name:
        Optional display name as presented by the provider.
    avatar_url:
        Optional URL to the author's avatar image.
    metadata:
        Optional free-form metadata captured from the provider payload.
    """

    external_id: str
    handle: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(slots=True)
class Media:
    """Canonical media metadata associated with a post.

    Attributes
    ----------
    kind:
        Media kind (e.g., ``"image"``, ``"video"``).
    url:
        Public URL for the media resource.
    mime_type:
        Optional MIME type associated with the media.
    width / height:
        Optional pixel dimensions of the media.
    duration_ms:
        Optional duration in milliseconds for time-based media.
    thumbnail_url:
        Optional URL of a preview thumbnail.
    alt_text:
        Optional alternative text for accessibility.
    metadata:
        Optional free-form metadata captured from the provider payload.
    """

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
    """Canonical entities extracted from the post text and payload.

    Attributes
    ----------
    hashtags:
        List of normalized hashtag strings (without the leading ``#``).
    mentions:
        List of mappings describing mentions (handle and/or external_id).
    links:
        List of link descriptors (URL and optional metadata).
    media:
        List of :class:`Media` objects describing attached media.
    """

    hashtags: Sequence[str]
    mentions: Sequence[Mapping[str, str | None]]
    links: Sequence[Mapping[str, Any]]
    media: Sequence[Media]


@dataclass(slots=True)
class Metrics:
    """Canonical counters associated with the post.

    Attributes
    ----------
    like_count / reply_count / repost_count / quote_count:
        Optional non-negative counters, omitted when the provider does not
        expose the metric.
    view_count / bookmark_count:
        Optional non-negative counters specific to some providers.
    score:
        Optional ranking score.
    extra:
        Optional provider-specific metrics not covered by the canonical
        attributes.
    """

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
    """Canonical representation of a social media post.

    Attributes
    ----------
    provider:
        Logical provider name (e.g., ``"bluesky"``).
    external_id:
        Stable provider-specific post identifier used for deduplication.
    created_at / collected_at:
        UTC timestamps for content creation and local collection instants.
    author:
        Canonical author information.
    text:
        Raw textual content as obtained from the provider.
    lang:
        Optional language code associated with the content.
    metrics:
        Optional counters as :class:`Metrics`.
    entities:
        Optional extracted entities as :class:`Entities`.
    visibility:
        Optional visibility label when provided by the network.
    in_reply_to / repost_of / quote_of:
        Optional lightweight references to related posts.
    source:
        Optional scope label used for collection.
    raw:
        Optional fragment of the original payload considered relevant.
    """

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
    """Options used to configure a provider session.

    Attributes
    ----------
    auth:
        Optional authentication material (e.g., API keys or tokens).
    http:
        Optional HTTP transport settings (e.g., timeouts or retries).
    hints:
        Optional operational hints influencing provider behavior.
    scope_defaults:
        Optional default values applied to collection scopes.
    """

    auth: Mapping[str, Any] | None = None
    http: Mapping[str, Any] | None = None
    hints: Mapping[str, Any] | None = None
    scope_defaults: Mapping[str, Any] | None = None


@dataclass(slots=True)
class ProviderSession:
    """Session metadata returned by a provider ``configure`` call.

    Attributes
    ----------
    provider:
        Logical provider name.
    auth_state:
        Authentication state label (e.g., ``"anonymous"`` or ``"authenticated"``).
    capabilities:
        Capability map describing supported features.
    rate_limit_policy:
        Optional known rate-limit parameters (requests per minute, burst, etc.).
    defaults:
        Optional default values like maximum page size.
    warnings:
        Optional list of warnings emitted during configuration.
    """

    provider: str
    auth_state: str
    capabilities: Mapping[str, Any]
    rate_limit_policy: Mapping[str, Any] | None
    defaults: Mapping[str, Any] | None
    warnings: Sequence[str]


@dataclass(slots=True)
class FetchBatch:
    """Normalized batch returned by a provider ``fetch_since`` call.

    Attributes
    ----------
    items:
        Sequence of normalized :class:`Post` items.
    next_cursor:
        Opaque cursor for the next page, or ``None`` when exhausted.
    reached_until:
        ``True`` when the batch reached the requested upper time bound.
    ignored_filters:
        List of filter names ignored due to lack of support.
    stats:
        Summary statistics for the batch (e.g., count, time window).
    rate_limit:
        Optional rate-limit snapshot when available from the provider.
    warnings:
        Optional list of warnings emitted during the fetch.
    """

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
        """Initialize the provider session.

        Parameters
        ----------
        options:
            Configuration material and operational hints.

        Returns
        -------
        ProviderSession
            Session metadata describing capabilities and defaults.
        """

        raise NotImplementedError

    def fetch_since(self, cursor: str | None, limit: int, filters: Mapping[str, Any]) -> FetchBatch:  # pragma: no cover - interface only
        """Fetch a normalized batch since the given cursor.

        Parameters
        ----------
        cursor:
            Opaque provider cursor from a previous call, or ``None`` to start.
        limit:
            Maximum desired number of items in this batch.
        filters:
            Optional filter mapping. Unsupported keys may be ignored.

        Returns
        -------
        FetchBatch
            Normalized items and the next cursor (if any).
        """

        raise NotImplementedError
