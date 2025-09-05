"""Minimal CLI placeholder for entry point compatibility.

The CLI is not part of the initial implementation phase. This file exists
to satisfy the configured entry point in ``pyproject.toml`` and will be
extended in later iterations.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """Entry point placeholder.

    Parameters
    ----------
    argv:
        Optional list of command-line arguments. When ``None``, ``sys.argv``
        is used.

    Returns
    -------
    int
        Process exit code, ``0`` on success.
    """

    _ = argv or sys.argv[1:]
    print("sonec CLI is not implemented yet. Please use the Python API.")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    raise SystemExit(main())

