"""Registre des outils disponibles pour M.A.L.I.E.C.A."""

from app.tools.base import Tool


class ToolRegistry:
    """Stocke et retrouve les outils disponibles."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Ajoute un outil au registre."""
        if tool.name in self._tools:
            raise ValueError(f"L'outil '{tool.name}' existe déjà.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """Récupère un outil grâce à son nom."""
        try:
            return self._tools[name]
        except KeyError as error:
            raise KeyError(f"L'outil '{name}' n'existe pas.") from error

    def list_tools(self) -> list[Tool]:
        """Renvoie la liste des outils enregistrés."""
        return list(self._tools.values())
