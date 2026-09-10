"""Command-line interface for M.A.L.I.E.C.A."""

from app.core.assistant import Assistant


def run_cli() -> None:
    """Run the interactive command-line assistant."""
    assistant = Assistant()
    print(f"{assistant.name} — mode conversation")
    print("Tapez 'quit' pour quitter.")

    while True:
        message = input("> ")
        if message.strip().lower() in {"quit", "exit"}:
            print("Arrêt de M.A.L.I.E.C.A.")
            return
        print(assistant.respond(message))
