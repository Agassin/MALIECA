"""Modèles utilisés par le cœur de M.A.L.I.E.C.A."""

from dataclasses import dataclass, field

from app.ai.base import AIMessage, ToolCall


@dataclass
class ConversationContext:
    """Mémoire de travail de la conversation en cours."""

    messages: list[AIMessage] = field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        """Ajoute un message de l'utilisateur au contexte."""
        self.messages.append(AIMessage(role="user", content=content))

    def add_assistant_message(
        self,
        content: str,
        tool_calls: tuple[ToolCall, ...] = (),
    ) -> None:
        """Ajoute un message de M.A.L.I.E.C.A. au contexte."""
        self.messages.append(
            AIMessage(role="assistant", content=content, tool_calls=tool_calls)
        )

    def add_tool_message(self, content: str, tool_call_id: str) -> None:
        """Ajoute le résultat d'un outil au contexte."""
        self.messages.append(
            AIMessage(role="tool", content=content, tool_call_id=tool_call_id)
        )
