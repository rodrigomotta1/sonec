from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Provider",
            fields=[
                ("name", models.CharField(primary_key=True, serialize=False, max_length=50)),
                ("version", models.CharField(blank=True, null=True, max_length=50)),
                ("capabilities", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "verbose_name": "Provider",
                "verbose_name_plural": "Providers",
            },
        ),
        migrations.CreateModel(
            name="Source",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("descriptor", models.CharField(max_length=255)),
                ("label", models.CharField(blank=True, null=True, max_length=255)),
                (
                    "provider",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.provider"),
                ),
            ],
            options={
                "verbose_name": "Source",
                "verbose_name_plural": "Sources",
            },
        ),
        migrations.CreateModel(
            name="Author",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("external_id", models.CharField(max_length=255)),
                ("handle", models.CharField(blank=True, null=True, max_length=255)),
                ("display_name", models.CharField(blank=True, null=True, max_length=255)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                (
                    "provider",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.provider"),
                ),
            ],
            options={
                "verbose_name": "Author",
                "verbose_name_plural": "Authors",
            },
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("external_id", models.CharField(max_length=255)),
                ("text", models.TextField()),
                ("lang", models.CharField(blank=True, null=True, max_length=16)),
                ("created_at", models.DateTimeField()),
                ("collected_at", models.DateTimeField()),
                ("metrics", models.JSONField(blank=True, default=dict)),
                ("entities", models.JSONField(blank=True, default=dict)),
                (
                    "author",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="core.author"),
                ),
                (
                    "provider",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.provider"),
                ),
            ],
            options={
                "verbose_name": "Post",
                "verbose_name_plural": "Posts",
            },
        ),
        migrations.CreateModel(
            name="Media",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("kind", models.CharField(max_length=16)),
                ("url", models.TextField()),
                ("metadata", models.JSONField(blank=True, default=dict)),
                (
                    "post",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="media", to="core.post"),
                ),
            ],
            options={
                "verbose_name": "Media",
                "verbose_name_plural": "Media",
            },
        ),
        migrations.CreateModel(
            name="FetchJob",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("started_at", models.DateTimeField()),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(max_length=32)),
                ("stats", models.JSONField(blank=True, default=dict)),
                (
                    "provider",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.provider"),
                ),
                (
                    "source",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.source"),
                ),
            ],
            options={
                "verbose_name": "Fetch Job",
                "verbose_name_plural": "Fetch Jobs",
            },
        ),
        migrations.CreateModel(
            name="Cursor",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("position", models.JSONField(default=dict)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "provider",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.provider"),
                ),
                (
                    "source",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.source"),
                ),
            ],
            options={
                "verbose_name": "Cursor",
                "verbose_name_plural": "Cursors",
            },
        ),
        migrations.AddConstraint(
            model_name="source",
            constraint=models.UniqueConstraint(fields=("provider", "descriptor"), name="uq_source_provider_descriptor"),
        ),
        migrations.AddConstraint(
            model_name="author",
            constraint=models.UniqueConstraint(fields=("provider", "external_id"), name="uq_author_provider_external_id"),
        ),
        migrations.AddConstraint(
            model_name="post",
            constraint=models.UniqueConstraint(fields=("provider", "external_id"), name="uq_post_provider_external_id"),
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(fields=["provider", "created_at"], name="post_provider_created_at_idx"),
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(fields=["author", "created_at"], name="post_author_created_at_idx"),
        ),
        migrations.AddConstraint(
            model_name="cursor",
            constraint=models.UniqueConstraint(fields=("provider", "source"), name="uq_cursor_provider_source"),
        ),
    ]

