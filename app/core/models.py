"""Modèles utilisés par le cœur de M.A.L.I.E.C.A."""

from dataclasses import dataclass, field

from app.ai.base import AIMessage


@dataclass
class ConversationContext:
    """Mémoire de travail de la conversation en cours."""

    messages: list[AIMessage] = field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        """Ajoute un message de l'utilisateur au contexte."""
        self.messages.append(AIMessage(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        """Ajoute un message de M.A.L.I.E.C.A. au contexte."""
        self.messages.append(AIMessage(role="assistant", content=content))
