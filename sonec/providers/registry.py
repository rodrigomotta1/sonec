"""Provider registry utilities.

This module maintains a mapping between provider names and their implementing
classes. It exposes functions to query, register and resolve providers.
"""

from __future__ import annotations

from typing import Dict, List, Type

from .base import Provider
from .bluesky import BlueskyProvider


_REGISTRY: Dict[str, Type[Provider]] = {
    "bluesky": BlueskyProvider,
}


def available() -> List[str]:
    """Return the list of registered provider names.

    Returns
    -------
    list[str]
        Provider names sorted alphabetically.
    """

    return sorted(_REGISTRY.keys())


def has(name: str) -> bool:
    """Return whether a provider name is registered.

    Parameters
    ----------
    name:
        Provider name to check.

    Returns
    -------
    bool
        ``True`` if the provider is registered; ``False`` otherwise.
    """

    return name.lower() in _REGISTRY


def register(name: str, provider_cls: Type[Provider], *, override: bool = False) -> None:
    """Register a provider class under a given name.

    Parameters
    ----------
    name:
        Logical provider name.
    provider_cls:
        Class object implementing the :class:`~sonec.providers.base.Provider` interface.
    override:
        When ``True``, replaces an existing registration. When ``False``,
        raises :class:`ValueError` if the name is already registered.

    Raises
    ------
    ValueError
        If ``override`` is ``False`` and a provider is already registered
        under ``name``.
    """

    key = name.lower()
    if not override and key in _REGISTRY:
        raise ValueError(f"Provider '{name}' is already registered")
    if not issubclass(provider_cls, Provider):  # type: ignore[arg-type]
        raise TypeError("provider_cls must be a subclass of Provider")
    _REGISTRY[key] = provider_cls


def unregister(name: str) -> None:
    """Remove a provider registration.

    Parameters
    ----------
    name:
        Provider name to unregister.

    Raises
    ------
    KeyError
        If the provider name is not registered.
    """

    key = name.lower()
    if key not in _REGISTRY:
        raise KeyError(f"Provider '{name}' is not registered")
    del _REGISTRY[key]


def resolve(name: str) -> Provider:
    """Resolve and instantiate a provider by name.

    Parameters
    ----------
    name:
        Logical provider name to resolve.

    Returns
    -------
    Provider
        An instance of the registered provider class.

    Raises
    ------
    KeyError
        If the provider name is not registered.
    """

    key = name.lower()
    try:
        cls = _REGISTRY[key]
    except KeyError as exc:  # pragma: no cover - trivial
        raise KeyError(f"No provider registered for name: {name}") from exc
    return cls()

