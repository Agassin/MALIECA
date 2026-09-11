"""Public assistant facade."""

from app.ai.base import AIModel
from app.core.runtime import Runtime


class Assistant:
    """Public entry point for interacting with M.A.L.I.E.C.A."""

    def __init__(
        self,
        name: str = "M.A.L.I.E.C.A.",
        model: AIModel | None = None,
    ) -> None:
        self.name = name
        self._nb_messages = 0
        self.runtime = Runtime(model=model)

    def respond(self, message: str) -> str:
        """Send a message through the assistant runtime."""
        self._nb_messages += 1
        return self.runtime.respond(message, self.name)
