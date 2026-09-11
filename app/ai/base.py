"""Base pour les modèles IA utilisés par M.A.L.I.E.C.A."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AIToolDefinition:
    """Description d'un outil présentée au modèle IA."""

    name: str
    description: str
    risk_level: int


@dataclass(frozen=True)
class ToolCall:
    """Demande d'exécution d'un outil formulée par le modèle IA."""

    id: str
    name: str
    arguments: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class AIMessage:
    """Message envoyé ou reçu par le modèle IA."""

    role: str
    content: str
    tool_calls: tuple[ToolCall, ...] = ()
    tool_call_id: str | None = None


@dataclass(frozen=True)
class AIResponse:
    """Réponse normalisée renvoyée par un modèle IA."""

    content: str
    metadata: dict[str, object] = field(default_factory=dict)
    tool_calls: tuple[ToolCall, ...] = ()


class AIModel(ABC):
    """Contrat que chaque modèle IA devra respecter."""

    @abstractmethod
    def generate(
        self,
        messages: list[AIMessage],
        tools: list[AIToolDefinition] | None = None,
    ) -> AIResponse:
        """Demande au modèle de générer une réponse ou des appels d'outils."""
        raise NotImplementedError
