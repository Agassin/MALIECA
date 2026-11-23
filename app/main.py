"""Application entry point for M.A.L.I.E.C.A."""

from app.interfaces.cli import run_cli


def main(argv: list[str] | None = None) -> None:
    """Start the assistant."""
    run_cli(argv)


if __name__ == "__main__":
    main()
