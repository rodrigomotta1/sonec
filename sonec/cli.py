"""Command-line interface for the sonec project.

This CLI currently exposes the ``init`` command to set up the local
runtime (SQLite) and apply database migrations. Additional commands
will be added in future iterations (collect, status, query).
"""

from __future__ import annotations

import sys
from typing import Optional

import typer

from . import api


app = typer.Typer(help="sonec command-line interface", no_args_is_help=True)


@app.command()
def init(
    db: Optional[str] = typer.Option(
        "sqlite:///./sonec.sqlite3",
        help="Database URL. Defaults to embedded SQLite at ./sonec.sqlite3",
    ),
) -> None:
    """Initialize the runtime and database.

    When no database URL is given, a local SQLite file (``./sonec.sqlite3``)
    is used. This command applies database migrations and prepares the
    environment for subsequent operations.
    """

    info = api.configure(db)
    typer.echo(f"Initialized sonec runtime: backend={info.backend} database={info.database}")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Parameters
    ----------
    argv:
        Optional list of command-line arguments.

    Returns
    -------
    int
        Process exit code, ``0`` on success.
    """
    args = argv if argv is not None else sys.argv[1:]
    try:
        # Explicitly forward args to Typer for robustness across wrappers
        app(args=args)
        return 0
    except SystemExit as exc:  # Typer may raise SystemExit
        return int(exc.code or 0)


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    raise SystemExit(main())
