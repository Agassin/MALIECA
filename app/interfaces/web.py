"""Interface et API JSON à usage local, servies sur l'adresse de bouclage."""

import json
import secrets
import sqlite3
from contextlib import closing
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from threading import Lock

from app.ai.base import AIModel
from app.core.session import LocalSession
from app.memory.store import MemoryStore

MAX_BODY = 32 * 1024
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


class LocalWebServer(ThreadingHTTPServer):
    def __init__(self, port: int, model: AIModel | None, label: str, db_path: Path) -> None:
        super().__init__(("127.0.0.1", port), LocalHandler)
        self.token = secrets.token_urlsafe(32)
        self.model = model
        self.label = label
        self.db_path = db_path
        self.model_lock = Lock()
        self.address = f"127.0.0.1:{self.server_port}"

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(10)
        return connection, address


class LocalHandler(BaseHTTPRequestHandler):
    server: LocalWebServer

    def do_GET(self) -> None:
        if not self._check_host():
            return
        if self.path == "/api/history":
            if not self._authorized():
                return
            try:
                memory = MemoryStore.open(self.server.db_path)
                with closing(memory.connection):
                    history = memory.recent_messages()
            except (OSError, sqlite3.Error):
                self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Base locale inaccessible."})
                return
            self._json(HTTPStatus.OK, {
                "engine": self.server.label,
                "messages": [{"role": message.role, "text": message.content} for message in history],
            })
            return

        asset = ASSETS.get(self.path)
        if asset is None:
            self._json(HTTPStatus.NOT_FOUND, {"error": "Page inconnue."})
            return
        filename, media_type = asset
        body = files("app.interfaces").joinpath("web_assets", filename).read_bytes()
        if self.path == "/":
            body = body.replace(b"{{TOKEN}}", self.server.token.encode("ascii"))
        self._send(HTTPStatus.OK, body, media_type)

    def do_POST(self) -> None:
        if not self._check_host() or not self._authorized():
            return
        if self.path != "/api/input":
            self._json(HTTPStatus.NOT_FOUND, {"error": "Route inconnue."})
            return
        if self.headers.get_content_type() != "application/json":
            self._json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "JSON requis."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_BODY:
                self._json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "Taille JSON invalide."})
                return
            body = json.loads(self.rfile.read(size))
            message = body.get("message") if isinstance(body, dict) else None
            if not isinstance(message, str) or not message.strip():
                raise ValueError
        except (OSError, ValueError):
            self._json(HTTPStatus.BAD_REQUEST, {"error": "Message JSON invalide."})
            return

        if not self.server.model_lock.acquire(blocking=False):
            self._json(HTTPStatus.CONFLICT, {"error": "Une demande est déjà en cours."})
            return
        try:
            memory = MemoryStore.open(self.server.db_path)
            with closing(memory.connection):
                result = LocalSession(self.server.model, memory).submit(message)
        except (OSError, ValueError, RuntimeError, sqlite3.Error) as error:
            self._json(HTTPStatus.UNPROCESSABLE_ENTITY, {"error": str(error)})
        else:
            self._json(HTTPStatus.OK, {"reply": result})
        finally:
            self.server.model_lock.release()

    def _check_host(self) -> bool:
        if self.headers.get("Host") == self.server.address:
            return True
        self._json(HTTPStatus.FORBIDDEN, {"error": "Adresse locale requise."})
        return False

    def _authorized(self) -> bool:
        expected = f"Bearer {self.server.token}".encode("ascii")
        actual = self.headers.get("Authorization", "").encode("latin-1")
        if secrets.compare_digest(actual, expected):
            return True
        self._json(HTTPStatus.FORBIDDEN, {"error": "Session locale requise."})
        return False

    def _json(self, status: HTTPStatus, data: dict[str, object]) -> None:
        self._send(status, json.dumps(data, ensure_ascii=False).encode(), "application/json")

    def _send(self, status: HTTPStatus, body: bytes, media_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", media_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
            "frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
        )
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        # Les échanges personnels restent dans la base et hors des journaux HTTP.
        return


def serve_web(port: int, model: AIModel | None, label: str, db_path: Path) -> None:
    with LocalWebServer(port, model, label, db_path) as server:
        print(f"M.A.L.I.E.C.A. est disponible sur http://{server.address}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nArrêt de M.A.L.I.E.C.A.")
