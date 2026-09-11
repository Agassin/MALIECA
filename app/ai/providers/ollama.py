"""Adaptateur pour utiliser un modèle local avec Ollama."""

import json
from urllib import error, request

from app.ai.base import AIMessage, AIModel, AIResponse, AIToolDefinition


class OllamaModel(AIModel):
    """Utilise l'API locale d'Ollama pour générer des réponses."""

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(
        self,
        messages: list[AIMessage],
        tools: list[AIToolDefinition] | None = None,
    ) -> AIResponse:
        """Envoie les messages à Ollama et récupère sa réponse."""
        del tools  # Le support natif du tool calling Ollama sera ajouté ensuite.

        payload = {
            "model": self.model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            "stream": False,
        }

        data = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            f"{self.base_url}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:
            raise RuntimeError(
                "Impossible de contacter Ollama. Vérifie qu'il est lancé."
            ) from exc

        content = result.get("message", {}).get("content")
        if not content:
            raise RuntimeError("Ollama a renvoyé une réponse sans contenu.")

        return AIResponse(
            content=content,
            metadata={"model": result.get("model", self.model)},
        )
