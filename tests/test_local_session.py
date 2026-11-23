from contextlib import closing

import pytest

from app.ai.base import AIMessage, AIModel, AIResponse, ToolCall
from app.core.session import LocalSession
from app.memory.store import MemoryStore


def test_task_note_and_document_commands_persist(tmp_path):
    path = tmp_path / "projet.sqlite3"
    document = tmp_path / "Projet été.md"
    document.write_text("Le projet d'été s'appelle Équinoxe.", encoding="utf-8")

    memory = MemoryStore.open(path)
    with closing(memory.connection):
        session = LocalSession(None, memory)
        assert "Tâche #1" in session.submit("/tache ajouter Préparer le test")
        assert "mise à jour" in session.submit("/tache modifier 1\tRelire les résultats")
        assert "mise à jour" in session.submit("/tache terminer 1")
        assert "Note #1" in session.submit("/note ajouter Langue préférée : français")
        assert "Document #1" in session.submit(f"/document importer {document}")

    memory = MemoryStore.open(path)
    with closing(memory.connection):
        session = LocalSession(None, memory)
        assert "[x] #1 Relire les résultats" in session.submit("/tache liste")
        assert "français" in session.submit("/note chercher prefere")
        assert "Équinoxe" in session.submit('/document chercher equinoxe" OR *')
        assert "mise à jour" in session.submit("/tache rouvrir 1")
        assert "[ ] #1" in session.submit("/tache liste")
        assert "supprimée" in session.submit("/tache supprimer 1")
        assert "supprimée" in session.submit("/note supprimer 1")
        assert "retiré" in session.submit("/document supprimer 1")
        assert session.submit("/document chercher equinoxe") == "Aucun passage trouvé."
        assert document.exists()


def test_document_reimport_replaces_old_passages_atomically(tmp_path):
    path = tmp_path / "note.md"
    path.write_text("marmotte", encoding="utf-8")
    memory = MemoryStore.open(tmp_path / "memory.sqlite3")
    with closing(memory.connection):
        first = memory.documents.import_file(path)
        path.write_text("hibou", encoding="utf-8")
        assert memory.documents.import_file(path) == first
        assert memory.documents.search("marmotte") == []
        assert memory.documents.search("hibou")[0].text == "hibou"


class NoteReader(AIModel):
    def generate(self, messages: list[AIMessage], tools=None) -> AIResponse:
        assert {"search_notes", "list_pending_tasks", "search_documents"} <= {
            tool.name for tool in tools
        }
        last = messages[-1]
        if last.content == "échouer":
            raise RuntimeError("échec simulé")
        if last.role == "user":
            return AIResponse("", tool_calls=(ToolCall("1", "search_notes", {"query": "école"}),))
        return AIResponse(last.content)


def test_failed_turn_is_discarded_and_tools_remain_read_only(tmp_path):
    memory = MemoryStore.open(tmp_path / "memory.sqlite3")
    with closing(memory.connection):
        session = LocalSession(NoteReader(), memory)
        session.submit("/note ajouter L'école ferme à 17 heures.")
        assert "ferme à 17 heures" in session.submit("Quand ferme l'école ?")
        assert [item.role for item in memory.recent_messages()] == ["user", "assistant"]

        with pytest.raises(RuntimeError, match="échec simulé"):
            session.submit("échouer")

        assert session.assistant.runtime.context.messages == memory.recent_messages()
        session.submit("/historique effacer")
        assert memory.recent_messages() == []
        assert memory.find_notes() != []
