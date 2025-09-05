"""Bluesky provider module.

Defines the interface for integration with Bluesky endpoints and the
normalization contract for returned batches.
"""

from __future__ import annotations

from typing import Mapping

from .base import FetchBatch, Provider, ProviderOptions, ProviderSession


class BlueskyProvider(Provider):
    """Provider implementation skeleton for Bluesky.

    The concrete ``configure`` and ``fetch_since`` implementations will be
    added in a subsequent iteration. This skeleton documents capabilities
    and expected interaction surfaces.
    """

    NAME = "bluesky"

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
        raise NotImplementedError("BlueskyProvider.fetch_since is not implemented.")
