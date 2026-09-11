"""Base pour les modèles IA utilisés par M.A.L.I.E.C.A."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AIMessage:
    """Message envoyé ou reçu par le modèle IA."""

    role: str
    content: str


@dataclass(frozen=True)
class AIResponse:
    """Réponse normalisée renvoyée par un modèle IA."""

    content: str
    metadata: dict[str, object] = field(default_factory=dict)


class AIModel(ABC):
    """Contrat que chaque modèle IA devra respecter."""

    @abstractmethod
    def generate(self, messages: list[AIMessage]) -> AIResponse:
        """Demande au modèle de générer une réponse."""
        raise NotImplementedError
