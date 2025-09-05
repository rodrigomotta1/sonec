from __future__ import annotations

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """App configuration for the canonical data model.

    The application label is ``core``.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "sonec.core"
    label = "core"

