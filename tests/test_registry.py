from __future__ import annotations

import pytest

from sonec.providers.base import Provider, ProviderOptions, ProviderSession, FetchBatch
from sonec.providers import bluesky
from sonec.providers.registry import available, resolve, register, unregister, has


class _DummyProvider(Provider):
    """Minimal dummy provider used for registry tests."""

    def configure(self, options: ProviderOptions) -> ProviderSession:  # pragma: no cover - trivial
        return ProviderSession(
            provider="dummy",
            auth_state="anonymous",
            capabilities={},
            rate_limit_policy=None,
            defaults=None,
            warnings=[],
        )

    def fetch_since(self, cursor, limit, filters):  # pragma: no cover - not exercised here
        raise NotImplementedError


def test_registry_contains_bluesky() -> None:
    names = available()
    assert "bluesky" in names
    prov = resolve("bluesky")
    assert isinstance(prov, bluesky.BlueskyProvider)


def test_register_and_unregister_dummy_provider() -> None:
    name = "dummy"
    # Ensure clean state
    if has(name):
        unregister(name)

    register(name, _DummyProvider)
    assert name in available()
    prov = resolve(name)
    assert isinstance(prov, _DummyProvider)

    # Duplicate without override should fail
    with pytest.raises(ValueError):
        register(name, _DummyProvider)

    # With override it must succeed
    register(name, _DummyProvider, override=True)

    # Unregister and ensure it's gone
    unregister(name)
    assert name not in available()

    # Unregistering again should raise
    with pytest.raises(KeyError):
        unregister(name)

    # Resolving unknown should raise
    with pytest.raises(KeyError):
        resolve(name)

