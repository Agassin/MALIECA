"""Moteur qui orchestre le fonctionnement de M.A.L.I.E.C.A."""

from app.ai.base import AIModel
from app.core.models import ConversationContext


class Runtime:
    """Gère le contexte et l'exécution du modèle IA."""

    def __init__(self, model: AIModel | None = None) -> None:
        self.model = model
        self.context = ConversationContext()

    def respond(self, message: str, assistant_name: str) -> str:
        """Traite un message et renvoie la réponse de M.A.L.I.E.C.A."""
        cleaned_message = message.strip()
        if not cleaned_message:
            return "Je n'ai pas reçu de demande."

        # On ajoute d'abord le message pour que le modèle ait accès au contexte.
        self.context.add_user_message(cleaned_message)

        # Tant qu'aucun vrai modèle n'est branché, on garde le comportement actuel.
        if self.model is None:
            response = f"{assistant_name} a reçu : {cleaned_message}"
        else:
            response = self.model.generate(self.context.messages).content

        # La réponse est également conservée pour les prochains messages.
        self.context.add_assistant_message(response)
        return response
