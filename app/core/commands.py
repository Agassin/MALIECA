"""Commandes explicites de gestion des données locales."""

from pathlib import Path

from app.memory.store import MemoryStore

HELP = """Commandes disponibles
  /note ajouter TEXTE         Enregistrer une note
  /note chercher [TEXTE]      Rechercher ou afficher les notes récentes
  /note supprimer ID          Supprimer une note
  /tache ajouter TITRE        Créer une tâche
  /tache liste               Afficher les tâches
  /tache modifier ID TITRE    Renommer une tâche
  /tache terminer ID          Cocher une tâche
  /tache rouvrir ID           Rouvrir une tâche
  /tache supprimer ID         Supprimer une tâche
  /document importer CHEMIN  Indexer un fichier texte UTF-8
  /document chercher TEXTE   Retrouver des passages indexés
  /document liste            Afficher les documents importés
  /document supprimer ID     Retirer un document de l'index
  /historique                Afficher les derniers échanges
  /historique effacer        Effacer la conversation enregistrée
  /aide                      Afficher ces commandes
  quit                       Quitter"""


def run_command(line: str, memory: MemoryStore) -> str:
    parts = (line.split(maxsplit=2) + ["", ""])[:3]
    command, action, argument = parts
    match command, action:
        case "/aide", "":
            return HELP
        case "/note", "ajouter":
            return f"Note #{memory.add_note(argument)} enregistrée."
        case "/note", "chercher":
            return "\n".join(
                f"#{note.id} {note.text}" for note in memory.find_notes(argument)
            ) or "Aucune note trouvée."
        case "/note", "supprimer":
            if memory.delete_note(parse_id(argument)):
                return "Note supprimée."
            return "Note introuvable."
        case "/tache", "ajouter":
            return f"Tâche #{memory.add_task(argument)} créée."
        case "/tache", "liste" if not argument:
            return "\n".join(
                f"[{'x' if task.done else ' '}] #{task.id} {task.title}"
                for task in memory.list_tasks()
            ) or "Aucune tâche."
        case "/tache", "modifier":
            task_id, *words = argument.split(maxsplit=1) or [""]
            title = words[0] if words else ""
            updated = memory.edit_task(parse_id(task_id), title)
        case "/tache", "terminer" | "rouvrir":
            updated = memory.set_task_done(parse_id(argument), action == "terminer")
        case "/tache", "supprimer":
            updated = memory.delete_task(parse_id(argument))
            return "Tâche supprimée." if updated else "Tâche introuvable."
        case "/document", "importer":
            if not argument:
                raise ValueError("Indiquez le chemin du document.")
            index = memory.documents
            return f"Document #{index.import_file(Path(argument))} indexé."
        case "/document", "chercher":
            passages = memory.documents.search(argument)
            return "\n\n".join(
                f"#{passage.document_id} {passage.title}, passage {passage.number}\n{passage.text}"
                for passage in passages
            ) or "Aucun passage trouvé."
        case "/document", "liste" if not argument:
            documents = memory.documents.list_documents()
            return "\n".join(f"#{number} {title}" for number, title in documents) or "Aucun document."
        case "/document", "supprimer":
            index = memory.documents
            return "Document retiré." if index.delete(parse_id(argument)) else "Document introuvable."
        case "/historique", "":
            return "\n".join(
                f"{'Vous' if message.role == 'user' else 'M.A.L.I.E.C.A.'} : {message.content}"
                for message in memory.recent_messages()
            ) or "Aucun échange enregistré."
        case "/historique", "effacer" if not argument:
            memory.clear_history()
            return "Historique effacé."
        case _:
            raise ValueError("Commande inconnue ou invalide. Tapez /aide.")

    return "Tâche mise à jour." if updated else "Tâche introuvable."


def parse_id(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise ValueError("Indiquez un identifiant numérique.") from None
    if not 1 <= number < 2**63:
        raise ValueError("Identifiant hors limites.")
    return number
