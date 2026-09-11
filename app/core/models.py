"""Domain models used by the assistant runtime."""

from dataclasses import dataclass, field

from app.ai.base import AIMessage


@dataclass
class ConversationContext:
    """Working memory for the current conversation."""

    messages: list[AIMessage] = field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        """Add a user message to the working context."""
        self.messages.append(AIMessage(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the working context."""
        self.messages.append(AIMessage(role="assistant", content=content))
