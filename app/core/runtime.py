"""Orchestration runtime for M.A.L.I.E.C.A."""

from app.ai.base import AIModel
from app.core.models import ConversationContext


class Runtime:
    """Coordinate conversation state and optional AI model execution."""

    def __init__(self, model: AIModel | None = None) -> None:
        self.model = model
        self.context = ConversationContext()

    def respond(self, message: str, assistant_name: str) -> str:
        """Process one user message and return the assistant response."""
        cleaned_message = message.strip()
        if not cleaned_message:
            return "Je n'ai pas reçu de demande."

        self.context.add_user_message(cleaned_message)

        if self.model is None:
            response = f"{assistant_name} a reçu : {cleaned_message}"
        else:
            response = self.model.generate(self.context.messages).content

        self.context.add_assistant_message(response)
        return response
