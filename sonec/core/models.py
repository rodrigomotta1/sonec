"""Canonical data models for sonec.

The models implement the normalized schema for providers, sources, authors,
posts, media, cursors and fetch jobs. All timestamps are stored in UTC, and
JSON fields are used for flexible metadata and metrics, maintaining portable
semantics across supported databases (SQLite in this version).
"""

from __future__ import annotations

from django.db import models


class Provider(models.Model):
    """Represents an origin social network and its operational capabilities.

    The natural key is the provider ``name`` which is stored as the primary
    key to simplify references throughout the schema.

    Attributes
    ----------
    name:
        Provider logical identifier used as primary key.
    version:
        Optional version label of the provider implementation.
    capabilities:
        Capability map describing supported features.
    """

    name: models.CharField = models.CharField(primary_key=True, max_length=50)
    version: models.CharField = models.CharField(max_length=50, blank=True, null=True)
    capabilities: models.JSONField = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Provider"
        verbose_name_plural = "Providers"

    def __str__(self) -> str:  # pragma: no cover - representation only
        return self.name


class Source(models.Model):
    """Defines a collection scope for a given provider.

    Examples include a handle, a query term, a list identifier, etc.
    The pair (provider, descriptor) must be unique.

    Attributes
    ----------
    provider:
        Foreign key to :class:`Provider`.
    descriptor:
        Scope identity within the provider (e.g., handle or query).
    label:
        Optional human-readable label.
    """

    provider: models.ForeignKey = models.ForeignKey(Provider, on_delete=models.CASCADE)
    descriptor: models.CharField = models.CharField(max_length=255)
    label: models.CharField = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = (("provider", "descriptor"),)
        verbose_name = "Source"
        verbose_name_plural = "Sources"

    def __str__(self) -> str:  # pragma: no cover - representation only
        return f"{self.provider}:{self.descriptor}"


class Author(models.Model):
    """Canonical author representation bound to a provider.

    Uniqueness is guaranteed by the pair (provider, external_id).

    Attributes
    ----------
    provider:
        Foreign key to :class:`Provider`.
    external_id:
        Stable author identifier within the provider.
    handle:
        Optional canonical handle (e.g., ``@alice``).
    display_name:
        Optional display name presented by the provider.
    metadata:
        Optional free-form metadata captured from the provider payload.
    """

    provider: models.ForeignKey = models.ForeignKey(Provider, on_delete=models.CASCADE)
    external_id: models.CharField = models.CharField(max_length=255)
    handle: models.CharField = models.CharField(max_length=255, blank=True, null=True)
    display_name: models.CharField = models.CharField(max_length=255, blank=True, null=True)
    metadata: models.JSONField = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = (("provider", "external_id"),)
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self) -> str:  # pragma: no cover - representation only
        return self.handle or self.external_id


class Post(models.Model):
    """Core entity representing a normalized social media post.

    Deduplication is enforced by the unique constraint on (provider, external_id).

    Attributes
    ----------
    id:
        Big auto-incremented primary key used for pagination ordering.
    provider:
        Foreign key to :class:`Provider`.
    external_id:
        Stable provider-specific post identifier.
    author:
        Foreign key to :class:`Author` (protected on delete).
    text:
        Post textual content.
    lang:
        Optional language code.
    created_at / collected_at:
        UTC timestamps for creation and local collection, respectively.
    metrics / entities:
        JSON structures holding counters and extracted entities.
    """

    id: models.BigAutoField = models.BigAutoField(primary_key=True)
    provider: models.ForeignKey = models.ForeignKey(Provider, on_delete=models.CASCADE)
    external_id: models.CharField = models.CharField(max_length=255)
    author: models.ForeignKey = models.ForeignKey(Author, on_delete=models.PROTECT)
    text: models.TextField = models.TextField()
    lang: models.CharField = models.CharField(max_length=16, blank=True, null=True)
    created_at: models.DateTimeField = models.DateTimeField()
    collected_at: models.DateTimeField = models.DateTimeField()
    metrics: models.JSONField = models.JSONField(default=dict, blank=True)
    entities: models.JSONField = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = (("provider", "external_id"),)
        indexes = [
            models.Index(fields=["provider", "created_at"], name="post_provider_created_at_idx"),
            models.Index(fields=["author", "created_at"], name="post_author_created_at_idx"),
        ]
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self) -> str:  # pragma: no cover - representation only
        return f"{self.provider}:{self.external_id}"


class Media(models.Model):
    """Metadata of media attached to a post.

    Binary content is not stored; only references and descriptive data.

    Attributes
    ----------
    post:
        Foreign key to :class:`Post`.
    kind:
        Media kind (e.g., ``image``, ``video``).
    url:
        Public URL referencing the media.
    metadata:
        Optional free-form metadata captured from the provider payload.
    """

    post: models.ForeignKey = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    kind: models.CharField = models.CharField(max_length=16)
    url: models.TextField = models.TextField()
    metadata: models.JSONField = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Media"
        verbose_name_plural = "Media"


class FetchJob(models.Model):
    """Represents a collection execution for diagnostics and auditing.

    Attributes
    ----------
    provider / source:
        Foreign keys to :class:`Provider` and :class:`Source` representing
        the collection scope.
    started_at / finished_at:
        UTC timestamps marking the job interval.
    status:
        Status label (e.g., ``running``, ``succeeded``, ``failed``).
    stats:
        JSON summary with counters and temporal windows.
    """

    provider: models.ForeignKey = models.ForeignKey(Provider, on_delete=models.CASCADE)
    source: models.ForeignKey = models.ForeignKey(Source, on_delete=models.CASCADE)
    started_at: models.DateTimeField = models.DateTimeField()
    finished_at: models.DateTimeField = models.DateTimeField(blank=True, null=True)
    status: models.CharField = models.CharField(max_length=32)
    stats: models.JSONField = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Fetch Job"
        verbose_name_plural = "Fetch Jobs"


class Cursor(models.Model):
    """Incremental position for collection continuity per (provider, source).

    Attributes
    ----------
    provider / source:
        Foreign keys to :class:`Provider` and :class:`Source` identifying
        the cursor scope.
    position:
        JSON structure storing the opaque cursor token or temporal marker.
    updated_at:
        Auto-updated timestamp indicating the last cursor change.
    """

    provider: models.ForeignKey = models.ForeignKey(Provider, on_delete=models.CASCADE)
    source: models.ForeignKey = models.ForeignKey(Source, on_delete=models.CASCADE)
    position: models.JSONField = models.JSONField(default=dict)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("provider", "source"),)
        verbose_name = "Cursor"
        verbose_name_plural = "Cursors"
