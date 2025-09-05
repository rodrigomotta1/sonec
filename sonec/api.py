"""Public Python API for the sonec project.

This module exposes high-level functions to configure the runtime, collect
data from providers, and query the canonical datastore using the normalized
schema defined by the project.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Literal, Sequence, Any, overload, TypedDict

import django
from django.conf import settings
from django.core.management import call_command
from django.db.models import Q, QuerySet

from .utils.time import parse_utc, to_rfc3339_z
from .utils.pagination import encode_after_key, decode_after_key


@dataclass(slots=True)
class RuntimeInfo:
    """Represents the initialized runtime information.

    Attributes
    ----------
    backend:
        The configured database backend label (e.g., ``"sqlite"``).
    database:
        The database name or path used by the configured backend. For SQLite,
        this is the filesystem path or ``":memory:"``.
    initialized:
        Indicates whether Django was configured and migrations were applied
        during the current process lifetime.
    """

    backend: str
    database: str
    initialized: bool


def _ensure_configured(db_url: str | None = None, *, additional_settings: dict | None = None) -> RuntimeInfo:
    """Configure Django settings programmatically if not already configured.

    Parameters
    ----------
    db_url:
        Database URL or path. Only SQLite is supported in this version. When
        ``None``, an in-memory SQLite database is used. Accepted forms include
        ``"sqlite://:memory:"``, ``"sqlite:///./sonec.sqlite3"`` or a direct
        path like ``"./sonec.sqlite3"``.
    additional_settings:
        Optional extra Django settings to merge with defaults. Keys follow
        Django's settings module conventions.

    Returns
    -------
    RuntimeInfo
        The runtime information describing the configured environment.
    """

    if settings.configured:  # Already configured by caller or test harness
        return RuntimeInfo(backend="sqlite", database=str(settings.DATABASES["default"]["NAME"]), initialized=True)

    database_name = ":memory:" if not db_url else db_url
    backend = "sqlite"

    # Accept values like "sqlite:///path" or just a filesystem path. For simplicity,
    # treat any non-empty string as the target name for SQLite.
    if database_name.startswith("sqlite://"):
        # Normalize common URL forms: sqlite:///path/to.db -> path/to.db
        # and sqlite://:memory:
        if database_name == "sqlite://:memory:":
            database_name = ":memory:"
        else:
            database_name = database_name.replace("sqlite:///", "")
    elif "://" in database_name and not database_name.startswith("sqlite://"):
        # Other backends are not supported in this iteration.
        raise ValueError("Only SQLite is supported in this version.")

    default_settings: dict = {
        "INSTALLED_APPS": [
            "django.contrib.contenttypes",
            "sonec.core",
        ],
        "DATABASES": {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": database_name,
            }
        },
        "USE_TZ": True,
        "TIME_ZONE": "UTC",
        "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
        "SECRET_KEY": "sonec-dev-secret-key",
        # Ensure pytest-django can clear the mailbox during tests.
        "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    }

    if additional_settings:
        default_settings.update(additional_settings)

    settings.configure(**default_settings)
    django.setup()

    # Apply migrations to create the schema of sonec.core
    call_command("migrate", run_syncdb=True, verbosity=0)

    # Ensure pytest-django can clear the mailbox even if no email was sent yet.
    # Locmem backend usually exposes ``django.core.mail.outbox``; define it when absent.
    try:  # pragma: no cover - side-effect for test environments
        from django.core import mail  # type: ignore

        if not hasattr(mail, "outbox"):
            mail.outbox = []  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - defensive
        pass

    return RuntimeInfo(backend=backend, database=str(database_name), initialized=True)


def configure(db_url: str | None = None, *, settings: dict | None = None) -> RuntimeInfo:
    """Initialize the runtime and database.

    This function configures Django programmatically and applies migrations
    for the canonical data model. Only SQLite is supported in this version.

    Parameters
    ----------
    db_url:
        Database URL or path. Examples: ``None`` (in-memory),
        ``"sqlite://:memory:"``, ``"sqlite:///./sonec.sqlite3"``,
        or a direct filesystem path like ``"./sonec.sqlite3"``.
    settings:
        Optional additional Django settings to merge with the defaults.
        This can be used to adjust logging, debugging or other runtime
        configuration during tests and scripts.

    Returns
    -------
    RuntimeInfo
        The runtime information about the configured environment.
    """

    return _ensure_configured(db_url, additional_settings=settings)


class QueryResultPage(TypedDict):
    """Typed mapping representing a paginated query result.

    Attributes
    ----------
    items:
        List of rows represented as dictionaries according to the selected
        projection.
    next_after_key:
        Opaque keyset token to retrieve the next page or ``None`` when there
        is no subsequent page.
    count:
        Number of items in this page.
    """

    items: list[dict[str, Any]]
    next_after_key: str | None
    count: int


def collect(
    *,
    provider: str,
    source: str | None = None,
    q: str | None = None,
    since_utc: datetime | str | None = None,
    until_utc: datetime | str | None = None,
    page_limit: int = 100,
    limit: int | None = None,
    window: timedelta | str | None = None,
    auth: bool | None = None,
    extras: dict | None = None,
) -> dict:
    """Collect data for a given provider and persist normalized items.

    This function orchestrates provider interaction, normalization and
    persistence according to the project contract.

    Not implemented; raises :class:`NotImplementedError`.

    Parameters
    ----------
    provider:
        Logical provider name (e.g., ``"bluesky"``) resolved via the provider
        registry.
    source:
        Optional scope identifier to collect from (e.g., a handle). Mutually
        exclusive with ``q``.
    q:
        Optional search query for providers that support search. Mutually
        exclusive with ``source``.
    since_utc / until_utc:
        Inclusive lower/upper time bounds applied by the provider when
        supported and filtered locally otherwise. Accepts ``datetime`` in UTC
        or RFC 3339 strings with ``Z`` suffix.
    page_limit:
        Maximum number of items per provider page request.
    limit:
        Overall maximum number of items to ingest for this call, or ``None``
        to collect until exhaustion or the ``until_utc`` boundary.
    window:
        Optional temporal window size to emulate pagination when a provider
        lacks native cursors.
    auth:
        Provider-specific authentication hint (e.g., request authenticated
        session). Details depend on the provider implementation.
    extras:
        Arbitrary provider-specific configuration.

    Returns
    -------
    dict
        A JSON-serializable report describing the collection outcome.
    """

    raise NotImplementedError("collect() is not implemented yet.")


@overload
def query(
    entity: Literal["posts", "authors", "jobs", "cursors"],
    *,
    provider: str | None = ...,
    since_utc: datetime | str | None = ...,
    until_utc: datetime | str | None = ...,
    author: str | None = ...,
    contains: str | None = ...,
    limit: int = ...,
    after_key: str | None = ...,
    project: Sequence[str] | None = ...,
    as_dict: Literal[True] = ...,  # type: ignore[assignment]
) -> QueryResultPage: ...


@overload
def query(
    entity: Literal["posts", "authors", "jobs", "cursors"],
    *,
    provider: str | None = ...,
    since_utc: datetime | str | None = ...,
    until_utc: datetime | str | None = ...,
    author: str | None = ...,
    contains: str | None = ...,
    limit: int = ...,
    after_key: str | None = ...,
    project: Sequence[str] | None = ...,
    as_dict: Literal[False],
) -> Iterable: ...


def query(
    entity: Literal["posts", "authors", "jobs", "cursors"],
    *,
    provider: str | None = None,
    since_utc: datetime | str | None = None,
    until_utc: datetime | str | None = None,
    author: str | None = None,
    contains: str | None = None,
    limit: int = 50,
    after_key: str | None = None,
    project: Sequence[str] | None = None,
    as_dict: bool = True,
) -> QueryResultPage | Iterable:
    """Query the canonical store and return a page of results.

    For ``entity == "posts"``, results are ordered by ``created_at DESC, id DESC``
    and paginated by keyset using ``after_key`` tokens.

    Parameters
    ----------
    entity:
        Target entity to query. Supported value: ``"posts"``.
    provider:
        Optional provider name filter (e.g., ``"bluesky"``).
    since_utc / until_utc:
        Inclusive lower/upper time bounds. Accept :class:`datetime.datetime`
        in UTC or RFC 3339 strings with ``Z`` suffix.
    author:
        Optional author selector. When prefixed with ``@``, matches the
        canonical ``handle``; otherwise matches ``external_id`` and, when
        numeric, the integer ``author_id``.
    contains:
        Full-text containment predicate on the canonical ``text``.
    limit:
        Maximum number of rows for the page.
    after_key:
        Opaque keyset token returned by a previous page, used to resume from
        the last seen row.
    project:
        Optional list of column names to include in the result rows when
        ``as_dict`` is ``True``.
    as_dict:
        When ``True``, returns a JSON-serializable mapping with items and
        pagination token. When ``False``, returns a list of ORM objects.

    Returns
    -------
    dict | Iterable
        When ``as_dict`` is ``True``, a mapping with the shape
        ``{"items": [...], "next_after_key": str | None, "count": int}``.
        Otherwise, a list of ORM objects for the selected entity.
    """

    if not settings.configured:
        raise RuntimeError("Django is not configured. Call sonec.api.configure() first.")

    if entity != "posts":
        raise NotImplementedError("Only 'posts' entity is supported.")

    from .core.models import Post  # Imported lazily to ensure settings are configured

    qs: QuerySet[Post] = Post.objects.select_related("provider", "author")

    if provider:
        qs = qs.filter(provider__name=provider)

    since_dt = parse_utc(since_utc)
    until_dt = parse_utc(until_utc)
    if since_dt is not None:
        qs = qs.filter(created_at__gte=since_dt)
    if until_dt is not None:
        qs = qs.filter(created_at__lte=until_dt)

    if author:
        if author.startswith("@"):
            qs = qs.filter(author__handle=author)
        else:
            # Try external_id; fall back to integer primary key when numeric
            q_author = Q(author__external_id=author)
            if author.isdigit():
                q_author |= Q(author_id=int(author))
            qs = qs.filter(q_author)

    if contains:
        qs = qs.filter(text__icontains=contains)

    # Order for keyset pagination
    qs = qs.order_by("-created_at", "-id")

    # Apply keyset
    if after_key:
        k = decode_after_key(after_key)
        qs = qs.filter(Q(created_at__lt=k.created_at) | (Q(created_at=k.created_at) & Q(id__lt=k.id)))

    # Fetch one extra row to determine if there is a next page
    rows = list(qs[: limit + 1])
    more = len(rows) > limit
    qs_page = rows[:limit]

    # Compute next_after_key only if more rows exist
    if not qs_page:
        next_token = None
    else:
        last = qs_page[-1]
        next_token = encode_after_key(last.created_at, last.id) if more else None

    if not as_dict:
        return qs_page

    # Projection helper
    def row_to_dict(p: Post) -> dict[str, Any]:
        base = {
            "id": p.id,
            "provider": p.provider_id,
            "external_id": p.external_id,
            "author_id": p.author_id,
            "created_at": p.created_at,
            "text": p.text,
            "lang": p.lang,
        }
        if project:
            return {k: base[k] for k in project if k in base}
        # Default projection
        return {k: base[k] for k in ("id", "provider", "external_id", "author_id", "created_at", "text")}

    items = [row_to_dict(p) for p in qs_page]
    return {"items": items, "next_after_key": next_token, "count": len(items)}


def status(*, provider: str | None = None, source: str | None = None, limit_jobs: int = 10) -> dict:
    """Return a summary of cursors and recent jobs.

    Not implemented; raises :class:`NotImplementedError`.

    Parameters
    ----------
    provider:
        Optional provider name filter to limit the snapshot.
    source:
        Optional source descriptor filter in combination with ``provider``.
    limit_jobs:
        Maximum number of recent jobs to include in the summary output.

    Returns
    -------
    dict
        A JSON-serializable mapping with cursors and jobs snapshot.
    """

    raise NotImplementedError("status() is not implemented yet.")
