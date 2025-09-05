from __future__ import annotations

from .cli import main as cli_main


def main() -> int:
    return cli_main()


if __name__ == "__main__":  # pragma: no cover - direct module execution
    raise SystemExit(main())

