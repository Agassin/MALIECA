"""Base pour tous les outils de M.A.L.I.E.C.A."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class ToolRisk(IntEnum):
    """Niveau de risque d'une action réalisée par un outil."""

    READ_ONLY = 0
    REVERSIBLE = 1
    LOCAL_MODIFICATION = 2
    EXTERNAL_ACTION = 3
    CRITICAL = 4


@dataclass(frozen=True)
class ToolResult:
    """Résultat renvoyé par un outil."""

    success: bool
    output: Any = None
    error: str | None = None


class Tool(ABC):
    """Contrat que chaque outil de M.A.L.I.E.C.A. doit respecter."""

    name: str
    description: str
    risk_level: ToolRisk

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        """Exécute l'outil avec les arguments reçus."""
        raise NotImplementedError
