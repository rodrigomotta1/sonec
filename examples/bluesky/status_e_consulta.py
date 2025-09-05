"""Exemplo: status e consulta de dados já coletados (Bluesky).

Este exemplo mostra como um pesquisador pode:

- Inicializar o banco via API (lendo `DATABASE_URL` quando presente).
- Ver um snapshot de status (cursors e últimos jobs) com `api.status(...)`.
- Executar consultas filtradas sobre `posts` com `api.query(...)` e projetar colunas.

Não realiza coleta; usa apenas os dados previamente persistidos.
"""

from __future__ import annotations

import argparse
import os
from typing import List, Optional

from sonec import api


def cmd_status(db_url: str, provider: Optional[str], source: Optional[str], limit_jobs: int) -> None:
    info = api.configure(db_url)
    print(f"[init] backend={info.backend} database={info.database}")

    snap = api.status(provider=provider, source=source, limit_jobs=limit_jobs)
    print("\nCursors:")
    for c in snap.get("cursors", []):
        print(f"  provider={c['provider']}  source={c['source']!r}  cursor={c['cursor']!s}  updated_at={c['updated_at']}")

    print("\nJobs:")
    for j in snap.get("jobs", []):
        print(
            "  id={id} provider={prov} source={src!r} started_at={sta} finished_at={fin} status={st} inserted={ins} conflicts={conf}".format(
                id=j.get("id"),
                prov=j.get("provider"),
                src=j.get("source"),
                sta=j.get("started_at"),
                fin=j.get("finished_at"),
                st=j.get("status"),
                ins=(j.get("stats") or {}).get("inserted"),
                conf=(j.get("stats") or {}).get("conflicts"),
            )
        )


def _parse_project(project: Optional[str]) -> Optional[List[str]]:
    if not project:
        return None
    cols = [c.strip() for c in project.split(",") if c.strip()]
    return cols or None


def cmd_query(
    db_url: str,
    provider: Optional[str],
    since: Optional[str],
    until: Optional[str],
    author: Optional[str],
    contains: Optional[str],
    limit: int,
    project: Optional[str],
) -> None:
    info = api.configure(db_url)
    print(f"[init] backend={info.backend} database={info.database}")

    cols = _parse_project(project)
    page = api.query(
        "posts",
        provider=provider,
        since_utc=since,
        until_utc=until,
        author=author,
        contains=contains,
        limit=limit,
        as_dict=True,
        project=cols,
    )

    items = page.get("items", [])
    print(f"\nResultados (count={page.get('count')}, next_after_key={page.get('next_after_key')}):")
    if not items:
        print("  <vazio>")
        return

    # Cabeçalho simples usando chaves da primeira linha
    keys = list(items[0].keys())
    print("  " + " | ".join(keys))
    for it in items:
        print("  " + " | ".join(str(it.get(k, "")) for k in keys))


def main() -> None:
    parser = argparse.ArgumentParser(description="Status e consulta de dados já coletados (Bluesky)")
    parser.add_argument(
        "--db",
        dest="db_url",
        default=os.environ.get("DATABASE_URL", "sqlite:///./sonec.sqlite3"),
        help="Database URL (padrão: DATABASE_URL ou SQLite local)",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_status = sub.add_parser("status", help="Snapshot de cursors e jobs recentes")
    p_status.add_argument("--provider", default=None, help="Filtrar por provider (ex.: bluesky)")
    p_status.add_argument("--source", default=None, help="Filtrar por source (com provider)")
    p_status.add_argument("--limit-jobs", dest="limit_jobs", type=int, default=10, help="Máx. de jobs listados")

    p_query = sub.add_parser("query", help="Consultar posts canônicos")
    p_query.add_argument("--provider", default=None, help="Filtrar por provider (ex.: bluesky)")
    p_query.add_argument("--since", default=None, help="Limite inferior de data/hora (ISO/RFC3339)")
    p_query.add_argument("--until", default=None, help="Limite superior de data/hora (ISO/RFC3339)")
    p_query.add_argument("--author", default=None, help="Autor (@handle, external_id ou id numérico)")
    p_query.add_argument("--contains", default=None, help="Filtro de substring no texto (case-insensitive)")
    p_query.add_argument("--limit", type=int, default=20, help="Limite de linhas da página")
    p_query.add_argument(
        "--project",
        default=None,
        help="Colunas projetadas, separadas por vírgula (ex.: id,created_at,text)",
    )

    args = parser.parse_args()

    if args.cmd == "status":
        cmd_status(args.db_url, args.provider, args.source, args.limit_jobs)
        return

    if args.cmd == "query":
        cmd_query(args.db_url, args.provider, args.since, args.until, args.author, args.contains, args.limit, args.project)
        return


if __name__ == "__main__":  # pragma: no cover - script manual
    main()

