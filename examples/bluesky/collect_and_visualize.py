"""Coleta e visualização (Bluesky).

O que faz
---------
- Configura o banco via API (usa `DATABASE_URL` quando presente; caso contrário, SQLite local).
- Coleta um lote por termo de busca (opcionalmente autenticado com App Password).
- Gera visualizações e salva arquivos PNG: série temporal (posts/dia), top autores e histograma de likes.

Como executar
-------------
1) Instale o projeto no ambiente ativo: `python -m pip install -e .`
2) (Recomendado) defina as credenciais do Bluesky na sessão:
   - PowerShell: `$env:BSKY_IDENTIFIER="seu-handle"; $env:BSKY_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"`
   - bash/zsh: `export BSKY_IDENTIFIER=...; export BSKY_APP_PASSWORD=...`
3) (Opcional) Instale a biblioteca de gráficos: `pip install matplotlib`
4) Execute a partir da raiz do repositório, por exemplo:
   - Com janela explícita: `python examples/bluesky/collect_and_visualize.py --q "termo" --since 2025-05-01T00:00:00Z --until 2025-05-07T23:59:59Z --limit-collect 1000`
   - Sem janela (usa `--days`): `python examples/bluesky/collect_and_visualize.py --q "termo" --days 14`

Resultados esperados
--------------------
- Relatório textual de coleta (itens inseridos, conflitos, cursor).
- PNGs salvos no diretório informado por `--out` (padrão: `examples/out`).
- Caso `matplotlib` não esteja instalado, o script segue e emite um resumo textual apenas.
"""

from __future__ import annotations

import argparse
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Tuple

from sonec import api
from sonec.utils.time import parse_utc


def _auth_extras_from_env() -> dict | None:
    ident = os.environ.get("BSKY_IDENTIFIER")
    pwd = os.environ.get("BSKY_APP_PASSWORD") or os.environ.get("BSKY_PASSWORD")
    if ident and pwd:
        return {"auth": {"identifier": ident, "password": pwd}}
    return None


def _collect(q: str, *, limit: int, page_limit: int, extras: dict | None, since: str | None, until: str | None) -> dict:
    return api.collect(
        provider="bluesky",
        q=q,
        limit=limit,
        page_limit=page_limit,
        extras=extras,
        since_utc=since,
        until_utc=until,
    )


def _query_posts(q: str, *, since: datetime | None, until: datetime | None, limit: int) -> Iterable[Any]:
    from sonec.core.models import Post

    qs = Post.objects.select_related("author", "provider").filter(provider_id="bluesky", text__icontains=q)
    if since is not None:
        qs = qs.filter(created_at__gte=since)
    if until is not None:
        qs = qs.filter(created_at__lte=until)
    return qs.order_by("-created_at", "-id")[:limit]


def _aggregate_time_series(q: str, *, since: datetime | None, until: datetime | None) -> list[tuple[datetime, int]]:
    from django.db.models import Count
    from django.db.models.functions import TruncDate
    from sonec.core.models import Post

    qs = Post.objects.filter(provider_id="bluesky", text__icontains=q)
    if since is not None:
        qs = qs.filter(created_at__gte=since)
    if until is not None:
        qs = qs.filter(created_at__lte=until)
    qs = qs.annotate(day=TruncDate("created_at")).values("day").annotate(n=Count("id")).order_by("day")
    out: list[tuple[datetime, int]] = []
    for row in qs:
        day = row["day"]
        n = int(row["n"])
        out.append((datetime(day.year, day.month, day.day, tzinfo=timezone.utc), n))
    return out


def _top_authors(q: str, *, since: datetime | None, until: datetime | None, k: int = 10) -> list[tuple[str, int]]:
    from django.db.models import Count
    from sonec.core.models import Post

    qs = Post.objects.filter(provider_id="bluesky", text__icontains=q)
    if since is not None:
        qs = qs.filter(created_at__gte=since)
    if until is not None:
        qs = qs.filter(created_at__lte=until)
    qs = qs.values("author__handle").annotate(n=Count("id")).order_by("-n")[:k]
    return [(row.get("author__handle") or "<unknown>", int(row["n"])) for row in qs]


def _likes_distribution(posts: Iterable[Any]) -> list[int]:
    likes: list[int] = []
    for p in posts:
        m = p.metrics or {}
        v = None
        if isinstance(m, dict):
            v = m.get("like_count")
        if isinstance(v, int) and v >= 0:
            likes.append(v)
    return likes


def _safe_slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", s).strip("_") or "term"


def _ensure_outdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _try_import_matplotlib():
    try:
        import matplotlib

        matplotlib.use("Agg")  # headless
        import matplotlib.pyplot as plt

        return plt
    except Exception:  # pragma: no cover - opcional
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Coleta e visualização profissional (Bluesky)")
    parser.add_argument("--q", "--query", dest="query", required=True, help="Termo de busca no Bluesky")
    parser.add_argument("--days", type=int, default=14, help="Janela em dias para análise (usada se --since/--until não forem informados)")
    parser.add_argument("--since", default=None, help="Limite inferior (ISO/RFC3339, ex.: 2025-05-01T00:00:00Z)")
    parser.add_argument("--until", default=None, help="Limite superior (ISO/RFC3339, ex.: 2025-05-31T23:59:59Z)")
    parser.add_argument("--limit-collect", dest="limit_collect", type=int, default=200, help="Máx. a coletar")
    parser.add_argument("--analysis-limit", dest="analysis_limit", type=int, default=2000, help="Máx. a carregar p/ análise")
    parser.add_argument("--page-limit", dest="page_limit", type=int, default=50, help="Itens por requisição ao provider")
    parser.add_argument("--db", dest="db_url", default=os.environ.get("DATABASE_URL", "sqlite:///./sonec.sqlite3"), help="URL do banco")
    parser.add_argument("--out", dest="out_dir", default="examples/out", help="Diretório de saída para gráficos")
    args = parser.parse_args()

    # 0) Configurar banco
    info = api.configure(args.db_url)
    print(f"[0/4] Banco pronto: backend={info.backend} db={info.database}")

    # 1) Coletar
    extras = _auth_extras_from_env()
    since_s = args.since
    until_s = args.until
    print(f"[1/4] Coletando: q='{args.query}' limit={args.limit_collect} page_limit={args.page_limit} since={since_s or '-'} until={until_s or '-'}")
    rep = _collect(args.query, limit=args.limit_collect, page_limit=args.page_limit, extras=extras, since=since_s, until=until_s)
    print(f"       -> inserted={rep['inserted']} conflicts={rep['conflicts']} last_cursor={rep['last_cursor']}")

    # 2) Consultar e agregar
    # Janela de análise: usa --since/--until quando presentes; caso contrário, usa --days retroativos
    since_dt = parse_utc(args.since) if args.since else (datetime.now(tz=timezone.utc) - timedelta(days=args.days))
    until_dt = parse_utc(args.until) if args.until else None
    posts = list(_query_posts(args.query, since=since_dt, until=until_dt, limit=args.analysis_limit))
    ts = _aggregate_time_series(args.query, since=since_dt, until=until_dt)
    top = _top_authors(args.query, since=since_dt, until=until_dt, k=10)
    likes = _likes_distribution(posts)

    print(f"[2/4] Dados para análise: posts={len(posts)} autores_top={len(top)} pontos_ts={len(ts)}")

    # 3) Visualizações (se matplotlib disponível)
    _ensure_outdir(args.out_dir)
    term = _safe_slug(args.query)
    plt = _try_import_matplotlib()
    if plt is None:
        print("[3/4] matplotlib não encontrado. Instale com 'pip install matplotlib' para gerar gráficos.")
    else:
        # Série temporal (posts/dia)
        if ts:
            x = [t for t, _ in ts]
            y = [n for _, n in ts]
            plt.figure(figsize=(9, 4))
            plt.plot(x, y, marker="o")
            plt.title(f"Bluesky: posts/dia (q='{args.query}')")
            plt.xlabel("Dia")
            plt.ylabel("# posts")
            plt.grid(True, alpha=0.3)
            fn = os.path.join(args.out_dir, f"ts_posts_{term}.png")
            plt.tight_layout(); plt.savefig(fn, dpi=120); plt.close()
            print(f"[3/4] Série temporal salva em: {fn}")

        # Top autores (por # posts)
        if top:
            labels = [h if h else "<unknown>" for h, _ in top]
            values = [n for _, n in top]
            plt.figure(figsize=(9, 4))
            plt.bar(range(len(values)), values)
            plt.xticks(range(len(labels)), labels, rotation=45, ha="right")
            plt.title(f"Bluesky: top autores (q='{args.query}')")
            plt.ylabel("# posts")
            plt.grid(axis="y", alpha=0.3)
            fn = os.path.join(args.out_dir, f"top_authors_{term}.png")
            plt.tight_layout(); plt.savefig(fn, dpi=120); plt.close()
            print(f"[3/4] Top autores salvo em: {fn}")

        # Histograma de likes
        if likes:
            plt.figure(figsize=(9, 4))
            plt.hist(likes, bins=20, color="#4472c4", alpha=0.85)
            plt.title(f"Bluesky: distribuição de likes (q='{args.query}')")
            plt.xlabel("likes")
            plt.ylabel("# posts")
            plt.grid(axis="y", alpha=0.3)
            fn = os.path.join(args.out_dir, f"likes_hist_{term}.png")
            plt.tight_layout(); plt.savefig(fn, dpi=120); plt.close()
            print(f"[3/4] Histograma de likes salvo em: {fn}")

    # 4) Resumo textual
    print("[4/4] Resumo")
    print("  Posts para análise:", len(posts))
    if top:
        print("  Top autores:")
        for h, n in top:
            print(f"    {h:>24}  posts={n}")
    if likes:
        print(f"  Likes (min/mediana/max): {min(likes)}/{sorted(likes)[len(likes)//2]}/{max(likes)}")


if __name__ == "__main__":  # pragma: no cover
    main()
