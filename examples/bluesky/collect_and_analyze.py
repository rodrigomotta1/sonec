"""Collect and analyze Bluesky posts by search term.

This example demonstrates how a researcher can use the sonec Python API to:

- Initialize the local datastore (SQLite by default) via ``sonec.api.configure``.
- Collect a small sample of posts from Bluesky using an arbitrary search term.
- Query the recent posts and produce a simple analysis: total likes per account.

Authentication
--------------
- Optional but recommended. Set these environment variables to use an App Password:
  - ``BSKY_IDENTIFIER``: your handle or email (e.g., ``alice.bsky.social``)
  - ``BSKY_APP_PASSWORD``: app password generated in Bluesky settings

Database
--------
- Uses ``DATABASE_URL`` when present (e.g., ``sqlite:///./sonec.sqlite3``),
  otherwise defaults to a local SQLite file at ``./sonec.sqlite3``.
"""

from __future__ import annotations

import argparse
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable

from sonec import api


def _collect_sample(keyword: str, *, limit: int = 100, page_limit: int = 25) -> dict:
    """Collect a small sample of Bluesky posts using a search query."""

    # Optional auth via env: BSKY_IDENTIFIER + BSKY_APP_PASSWORD
    auth_extras = None
    ident = os.environ.get("BSKY_IDENTIFIER")
    pwd = os.environ.get("BSKY_APP_PASSWORD") or os.environ.get("BSKY_PASSWORD")
    if ident and pwd:
        auth_extras = {"auth": {"identifier": ident, "password": pwd}}

    report = api.collect(
        provider="bluesky",
        q=keyword,
        limit=limit,
        page_limit=page_limit,
        extras=auth_extras,
    )
    return report


def _query_recent_posts(keyword: str, *, days: int = 14, limit: int = 500) -> Iterable[Any]:
    """Retrieve recent posts containing a keyword using ORM for analysis."""

    since = datetime.now(tz=timezone.utc) - timedelta(days=days)
    # Import models only after runtime configuration to avoid ImproperlyConfigured
    from sonec.core.models import Post

    qs = (
        Post.objects.select_related("author", "provider")
        .filter(provider_id="bluesky", text__icontains=keyword, created_at__gte=since)
        .order_by("-created_at", "-id")[:limit]
    )
    return qs


def _analyze_total_likes_by_account(posts: Iterable[Any]) -> Dict[str, int]:
    """Aggregate total likes per author handle from a sequence of posts."""

    totals: Dict[str, int] = defaultdict(int)
    for p in posts:
        handle = p.author.handle if p.author and p.author.handle else "<unknown>"
        like_count = 0
        metrics = p.metrics or {}
        if isinstance(metrics, dict):
            like_val = metrics.get("like_count")
            if isinstance(like_val, int) and like_val >= 0:
                like_count = like_val
        totals[handle] += like_count
    return dict(totals)


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect and analyze Bluesky posts by search term.")
    parser.add_argument("--q", "--query", dest="query", required=True, help="Search term or phrase for Bluesky search")
    parser.add_argument("--limit", type=int, default=100, help="Max posts to ingest")
    parser.add_argument("--page-limit", dest="page_limit", type=int, default=25, help="Max items per provider request")
    parser.add_argument("--days", type=int, default=14, help="Days window for analysis")
    parser.add_argument(
        "--analysis-limit", dest="analysis_limit", type=int, default=500, help="Max posts to load for analysis"
    )
    parser.add_argument(
        "--db",
        dest="db_url",
        default=os.environ.get("DATABASE_URL", "sqlite:///./sonec.sqlite3"),
        help="Database URL (defaults to DATABASE_URL or local SQLite)",
    )
    args = parser.parse_args()

    info = api.configure(args.db_url)
    print(f"[0/2] Initialized: backend={info.backend} database={info.database}")

    print(f"[1/2] Collecting sample from Bluesky (q='{args.query}')...")
    report = _collect_sample(args.query, limit=args.limit, page_limit=args.page_limit)
    print(f"  -> inserted={report['inserted']} conflicts={report['conflicts']} last_cursor={report['last_cursor']}")

    print("[2/2] Querying recent posts and analyzing likes per account...")
    recent_posts = list(_query_recent_posts(args.query, days=args.days, limit=args.analysis_limit))
    totals = _analyze_total_likes_by_account(recent_posts)

    print("\nSummary")
    print("-------")
    print(f"Posts analyzed: {len(recent_posts)}")
    print(f"Accounts found: {len(totals)}")

    top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:10]
    if not top:
        print("No results to display. Try increasing the time window or limit.")
        return

    print(f"\nTop accounts by total likes (mentioning '{args.query}'):")
    for handle, likes in top:
        print(f"  {handle:>24}  likes={likes}")


if __name__ == "__main__":  # pragma: no cover - example script
    main()

