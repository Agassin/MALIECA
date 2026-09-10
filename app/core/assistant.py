class Assistant:
    def __init__(self, name: str = "M.A.L.I.E.C.A.") -> None:
        self.name = name
        self._nb_messages = 0

    def respond(self, message: str) -> str:
        self._nb_messages += 1
        message = message.strip()
        if not message:
            return "Je n'ai pas reçu de demande."
        return f"{self.name} a reçu : {message}"
