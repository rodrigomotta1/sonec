"""Public Python API for the sonec project.

This module exposes high-level functions to configure the runtime, collect
data from providers, and query the canonical datastore. The initial
implementation focuses on the runtime setup and data model; collection and
query routines are scaffolds to be implemented in subsequent iterations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Literal, Sequence

import django
from django.conf import settings
from django.core.management import call_command


@dataclass(slots=True)
class RuntimeInfo:
    """Represents the initialized runtime information.

    Attributes
    ----------
    backend:
        The configured database backend label (e.g., ``"sqlite"``).
    database:
        The database name or path.
    initialized:
        Whether Django was configured and migrations were applied.
    """

    backend: str
    database: str
    initialized: bool


def _ensure_configured(db_url: str | None = None, *, additional_settings: dict | None = None) -> RuntimeInfo:
    """Configure Django settings programmatically if not already configured.

    Parameters
    ----------
    db_url:
        Database URL. Only SQLite is supported in this version. When ``None``,
        an in-memory SQLite database is used.
    additional_settings:
        Optional extra settings to merge with defaults.

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

    Returns
    -------
    RuntimeInfo
        The runtime information about the configured environment.
    """

    return _ensure_configured(db_url, additional_settings=settings)


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

    This is a scaffold function. The implementation will be provided in the
    next iteration together with the Bluesky provider integration.

    Returns
    -------
    dict
        A JSON-serializable report as specified in the implementation guide.
    """

    raise NotImplementedError("collect() is not implemented yet.")


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
) -> dict | Iterable:
    """Query the canonical store and return a page of results.

    This is a scaffold function. The implementation will be provided in the
    next iteration once the data model and provider ingestion are finalized.
    """

    raise NotImplementedError("query() is not implemented yet.")


def status(*, provider: str | None = None, source: str | None = None, limit_jobs: int = 10) -> dict:
    """Return a summary of cursors and recent jobs.

    This is a scaffold function. It will be implemented alongside collection
    and job/cursor tracking.
    """

    raise NotImplementedError("status() is not implemented yet.")
