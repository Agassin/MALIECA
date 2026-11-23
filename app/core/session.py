"""Point d'entrée partagé par les interfaces locales."""

from app.ai.base import AIModel
from app.core.assistant import Assistant
from app.core.commands import run_command
from app.memory.store import MemoryStore
from app.tools.builtin.memory import ListTasksTool, SearchDocumentsTool, SearchNotesTool


class LocalSession:
    def __init__(self, model: AIModel | None, memory: MemoryStore) -> None:
        self.assistant = Assistant(model=model)
        self.memory = memory
        registry = self.assistant.runtime.tool_registry
        registry.register(SearchNotesTool(memory))
        registry.register(ListTasksTool(memory))
        registry.register(SearchDocumentsTool(memory))

    def submit(self, message: str) -> str:
        message = message.strip()
        if not message:
            return ""
        if message.startswith("/"):
            return run_command(message, self.memory)
        runtime = self.assistant.runtime
        if runtime.model is None:
            return "Mode hors ligne. Tapez /aide pour les commandes locales."

        runtime.context.messages[:] = self.memory.recent_messages()
        response = self.assistant.respond(message)
        self.memory.save_turn(message, response)
        return response
