"""Bluesky provider skeleton.

This module will implement the Bluesky provider using the public endpoints
and return normalized batches according to the provider contract. The
current implementation serves as a scaffold for subsequent work.
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

    def configure(self, options: ProviderOptions) -> ProviderSession:  # pragma: no cover - placeholder
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

    def fetch_since(self, cursor: str | None, limit: int, filters: Mapping[str, object]) -> FetchBatch:  # pragma: no cover - placeholder
        raise NotImplementedError("BlueskyProvider.fetch_since is not implemented yet.")

