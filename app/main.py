"""Application entry point for M.A.L.I.E.C.A."""

from app.interfaces.cli import run_cli


def main() -> None:
    """Start the assistant."""
    run_cli()


if __name__ == "__main__":
    main()
