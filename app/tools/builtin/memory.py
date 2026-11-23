"""Outils de lecture des données personnelles, accessibles au modèle local."""

import json
from dataclasses import asdict
from typing import ClassVar

from app.memory.store import MemoryStore
from app.tools.base import Tool, ToolResult, ToolRisk


class SearchNotesTool(Tool):
    name = "search_notes"
    description = "Cherche un mot ou une expression dans les notes enregistrées par l'utilisateur."
    risk_level = ToolRisk.READ_ONLY
    parameters: ClassVar[dict[str, object]] = {
        "type": "object",
        "properties": {"query": {"type": "string", "minLength": 1, "maxLength": 256}},
        "required": ["query"],
        "additionalProperties": False,
    }

    def __init__(self, memory: MemoryStore) -> None:
        self.memory = memory

    def execute(self, arguments: dict[str, str]) -> ToolResult:
        notes = self.memory.find_notes(arguments["query"], limit=10)
        return ToolResult(True, json.dumps([asdict(note) for note in notes], ensure_ascii=False))


class ListTasksTool(Tool):
    name = "list_pending_tasks"
    description = "Liste les tâches qui restent à terminer."
    risk_level = ToolRisk.READ_ONLY
    parameters: ClassVar[dict[str, object]] = {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }

    def __init__(self, memory: MemoryStore) -> None:
        self.memory = memory

    def execute(self, arguments: dict[str, object]) -> ToolResult:
        tasks = self.memory.list_tasks(include_done=False)
        return ToolResult(True, json.dumps([asdict(task) for task in tasks], ensure_ascii=False))


class SearchDocumentsTool(Tool):
    name = "search_documents"
    description = (
        "Recherche des extraits dans les documents locaux importés. "
        "Utiliser quelques mots-clés significatifs et citer le titre et le numéro du passage."
    )
    risk_level = ToolRisk.READ_ONLY
    parameters: ClassVar[dict[str, object]] = SearchNotesTool.parameters

    def __init__(self, memory: MemoryStore) -> None:
        self.memory = memory

    def execute(self, arguments: dict[str, str]) -> ToolResult:
        passages = self.memory.documents.search(arguments["query"])
        return ToolResult(True, json.dumps([asdict(passage) for passage in passages], ensure_ascii=False))
