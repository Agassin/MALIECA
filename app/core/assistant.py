"""Main assistant orchestration logic."""


class Assistant:
    """Minimal assistant core that can later orchestrate tools and memory."""

    def __init__(self, name: str = "M.A.L.I.E.C.A.") -> None:
        self.name = name

    def respond(self, message: str) -> str:
        """Return a basic response while the real reasoning layer is built."""
        message = message.strip()
        if not message:
            return "Je n'ai pas reçu de demande."
        return f"{self.name} a reçu : {message}"
