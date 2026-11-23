"""Index textuel des documents explicitement importés."""

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

MAX_DOCUMENT_BYTES = 1024 * 1024
CHUNK_SIZE = 1200
OVERLAP = 160


@dataclass(frozen=True)
class Passage:
    document_id: int
    title: str
    number: int
    text: str


class DocumentIndex:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        try:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS passages USING fts5(
                    document_id UNINDEXED, number UNINDEXED, text,
                    tokenize='unicode61 remove_diacritics 2'
                );
            """)
        except sqlite3.OperationalError as error:
            if "no such module: fts5" in str(error).lower():
                raise RuntimeError("La recherche documentaire nécessite SQLite avec FTS5.") from error
            raise

    def import_file(self, path: Path) -> int:
        path = path.expanduser().resolve(strict=True)
        if path.suffix.lower() not in {".txt", ".md", ".rst"} or not path.is_file():
            raise ValueError("Choisissez un fichier texte UTF-8 (.txt, .md ou .rst).")
        with path.open("rb") as stream:
            raw = stream.read(MAX_DOCUMENT_BYTES + 1)
        if len(raw) > MAX_DOCUMENT_BYTES:
            raise ValueError("La taille du document dépasse 1 Mio.")
        text = raw.decode("utf-8-sig").strip()
        if not text or "\x00" in text:
            raise ValueError("Le document doit contenir du texte UTF-8 lisible.")

        with self.connection:
            row = self.connection.execute(
                """INSERT INTO documents (path, title) VALUES (?, ?)
                   ON CONFLICT (path) DO UPDATE SET title = excluded.title
                   RETURNING id""",
                (str(path), path.name),
            ).fetchone()
            document_id = row[0]
            self.connection.execute(
                "DELETE FROM passages WHERE document_id = ?", (document_id,)
            )
            self.connection.executemany(
                "INSERT INTO passages (document_id, number, text) VALUES (?, ?, ?)",
                ((document_id, number, chunk) for number, chunk in enumerate(split_text(text), 1)),
            )
        return document_id

    def search(self, query: str, limit: int = 5) -> list[Passage]:
        words = list(dict.fromkeys(re.findall(r"[^\W_]+", query.casefold())))[:16]
        if not words:
            return []
        expression = " OR ".join(f'"{word}"' for word in words)
        rows = self.connection.execute(
            """SELECT documents.id, documents.title, passages.number, passages.text
               FROM passages JOIN documents ON documents.id = passages.document_id
               WHERE passages MATCH ? ORDER BY rank, passages.rowid LIMIT ?""",
            (expression, limit),
        )
        return [Passage(*row) for row in rows]

    def list_documents(self) -> list[tuple[int, str]]:
        return self.connection.execute("SELECT id, title FROM documents ORDER BY id").fetchall()

    def delete(self, document_id: int) -> bool:
        with self.connection:
            self.connection.execute("DELETE FROM passages WHERE document_id = ?", (document_id,))
            result = self.connection.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        return result.rowcount == 1


def split_text(text: str):
    """Découpe près d'un séparateur et conserve un chevauchement pour le contexte."""
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        if end < len(text):
            boundary = max(text.rfind(separator, end - OVERLAP, end) for separator in ("\n", " "))
            if boundary > start:
                end = boundary
        yield text[start:end].strip()
        if end >= len(text):
            break
        start = end - OVERLAP
