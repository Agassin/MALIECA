"""Adaptateur pour utiliser un modèle local avec Ollama."""

import json
from urllib import error, request

from app.ai.base import AIMessage, AIModel, AIResponse, AIToolDefinition, ToolCall


class OllamaResponseError(RuntimeError):
    """La réponse HTTP ne respecte pas le contrat Ollama."""


class OllamaModel(AIModel):
    """Utilise l'API locale d'Ollama pour générer des réponses."""

    def __init__(
        self,
        model: str = "qwen3",
        base_url: str = "http://localhost:11434",
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        if not model.strip() or not self.base_url.startswith(("http://", "https://")):
            raise ValueError("Indiquez un modèle et une adresse Ollama HTTP ou HTTPS valides.")

    def generate(
        self,
        messages: list[AIMessage],
        tools: list[AIToolDefinition] | None = None,
    ) -> AIResponse:
        """Envoie les messages à Ollama et récupère sa réponse."""
        payload = {
            "model": self.model,
            "messages": [self._serialize_message(message) for message in messages],
            "stream": False,
        }
        if tools:
            payload["tools"] = [self._serialize_tool(tool) for tool in tools]

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
        except error.HTTPError as exc:
            try:
                with exc:
                    body = json.loads(exc.read(4096))
                detail = body.get("error") if isinstance(body, dict) else None
            except (OSError, ValueError):
                detail = None
            raise RuntimeError(f"Ollama (HTTP {exc.code}) : {detail or exc.reason}") from exc
        except (error.URLError, TimeoutError) as exc:
            raise RuntimeError(
                "Impossible de contacter Ollama. Vérifie qu'il est lancé."
            ) from exc

        except (ValueError, OSError) as exc:
            raise RuntimeError("Ollama a renvoyé une réponse illisible.") from exc

        message = result.get("message") if isinstance(result, dict) else None
        if not isinstance(message, dict):
            raise OllamaResponseError("Ollama a renvoyé un message invalide.")

        raw_calls = message.get("tool_calls") or []
        content = message.get("content", "")
        if not isinstance(content, str) or not isinstance(raw_calls, list):
            raise OllamaResponseError("Ollama a renvoyé un message invalide.")
        tool_calls = tuple(self._parse_tool_call(call, index) for index, call in enumerate(raw_calls))

        if not content and not tool_calls:
            raise RuntimeError("Ollama a renvoyé une réponse vide.")

        return AIResponse(
            content=content,
            metadata={"model": result.get("model", self.model)},
            tool_calls=tool_calls,
        )

    @staticmethod
    def _serialize_message(message: AIMessage) -> dict[str, object]:
        """Transforme un message interne au format attendu par Ollama."""
        serialized: dict[str, object] = {
            "role": message.role,
            "content": message.content,
        }
        if message.tool_calls:
            serialized["tool_calls"] = [
                {
                    "type": "function",
                    "function": {
                        "name": call.name,
                        "arguments": call.arguments,
                    },
                }
                for call in message.tool_calls
            ]
        if message.role == "tool" and message.tool_name:
            serialized["tool_name"] = message.tool_name
        return serialized

    @staticmethod
    def _serialize_tool(tool: AIToolDefinition) -> dict[str, object]:
        """Transforme une définition interne au format Ollama."""
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }

    @staticmethod
    def _parse_tool_call(call: dict[str, object], index: int) -> ToolCall:
        """Transforme un appel d'outil Ollama en appel interne."""
        function = call.get("function") if isinstance(call, dict) else None
        if not isinstance(function, dict):
            raise OllamaResponseError("Ollama a renvoyé un appel d'outil invalide.")

        name = function.get("name")
        arguments = function.get("arguments", {})
        if not isinstance(name, str) or not isinstance(arguments, dict):
            raise OllamaResponseError("Ollama a renvoyé un appel d'outil invalide.")

        return ToolCall(
            id=f"ollama-call-{index}",
            name=name,
            arguments=arguments,
        )
