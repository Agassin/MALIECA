"""Command-line interface for M.A.L.I.E.C.A."""

from app.ai.providers.ollama import OllamaModel
from app.core.assistant import Assistant


def run_cli() -> None:
    """Lance l'assistant avec le moteur Ollama temporaire."""
    assistant = Assistant(model=OllamaModel())
    print(f"{assistant.name} — mode conversation")
    print("Moteur : Ollama / qwen3")
    print("Tapez 'quit' pour quitter.")

    while True:
        message = input("> ")
        if message.strip().lower() in {"quit", "exit"}:
            print("Arrêt de M.A.L.I.E.C.A.")
            return
        try:
            print(assistant.respond(message))
        except RuntimeError as error:
            print(f"Erreur : {error}")
