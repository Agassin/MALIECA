"""Interface de conversation et de gestion des données locales."""

import sqlite3
from argparse import ArgumentParser
from contextlib import closing
from pathlib import Path

from app.ai.base import AIModel
from app.ai.providers.ollama import OllamaModel
from app.core.session import LocalSession
from app.interfaces.web import serve_web
from app.memory.store import MemoryStore


def run_cli(argv: list[str] | None = None) -> None:
    """Démarre la conversation avec un fournisseur local configurable."""
    parser = ArgumentParser(description="Assistant local M.A.L.I.E.C.A.")
    parser.add_argument("--db", type=Path, default=Path.home() / ".malieca" / "memory.sqlite3")
    parser.add_argument("--web", action="store_true", help="Servir l'interface web locale")
    parser.add_argument("--port", type=int, default=8765, help="Port de l'interface web")
    parser.add_argument("--model", default="qwen3", help="Nom du modèle Ollama")
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    engine = parser.add_mutually_exclusive_group()
    engine.add_argument("--offline", action="store_true", help="Commandes locales sans modèle")
    engine.add_argument("--checkpoint", type=Path, help="Checkpoint expérimental MALIECA-LLM")
    args = parser.parse_args(argv)

    if not 0 <= args.port <= 65535:
        parser.error("--port doit être compris entre 0 et 65535.")

    model: AIModel | None = None
    label = "commandes locales"
    try:
        if args.checkpoint:
            from app.ai.providers.malieca import MaliecaModel

            model = MaliecaModel.load(args.checkpoint)
            label = "MALIECA-LLM (expérimental)"
        elif not args.offline:
            model = OllamaModel(model=args.model, base_url=args.ollama_url)
            label = f"Ollama / {args.model}"
        memory = MemoryStore.open(args.db)
        with closing(memory.connection):
            if not args.web:
                _conversation(model, label, memory)
                return
        serve_web(args.port, model, label, args.db)
    except (ImportError, OSError, ValueError, RuntimeError, sqlite3.Error) as error:
        parser.exit(1, f"Erreur de démarrage : {error}\n")


def _conversation(model: AIModel | None, label: str, memory: MemoryStore) -> None:
    session = LocalSession(model, memory)
    print(f"{session.assistant.name} — mode conversation")
    print(f"Moteur : {label}")
    print("Tapez /aide pour les commandes et quit pour quitter.")

    while True:
        try:
            message = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if message.lower() in {"quit", "exit"}:
            break
        if not message:
            continue

        try:
            print(session.submit(message))
        except (OSError, RuntimeError, ValueError, sqlite3.Error) as error:
            print(f"Erreur : {error}")
        except KeyboardInterrupt:
            print("\nDemande interrompue.")

    print("Arrêt de M.A.L.I.E.C.A.")
