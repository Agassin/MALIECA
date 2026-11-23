import json
import re
from http.client import HTTPConnection
from threading import Thread

from app.interfaces.web import LocalWebServer


def test_web_api_checks_host_and_token_then_persists_local_commands(tmp_path):
    with LocalWebServer(0, None, "commandes locales", tmp_path / "memory.sqlite3") as server:
        worker = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
        worker.start()
        client = HTTPConnection(server.address, timeout=3)
        try:
            client.request("GET", "/", headers={"Host": "malieca.example"})
            response = client.getresponse()
            assert response.status == 403
            response.read()

            client.request("GET", "/")
            response = client.getresponse()
            assert response.status == 200
            assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
            token = re.search(rb'name="session-token" content="([^"]+)"', response.read())[1]

            client.request("GET", "/api/history")
            response = client.getresponse()
            assert response.status == 403
            response.read()

            headers = {"Authorization": b"Bearer " + token, "Content-Type": "application/json"}
            client.request("POST", "/api/input", json.dumps({"message": "/tache ajouter Vérifier"}), headers)
            response = client.getresponse()
            assert response.status == 200
            assert "Tâche #1" in json.load(response)["reply"]

            client.request("POST", "/api/input", '{"message": "/tache liste"}', headers)
            response = client.getresponse()
            assert json.load(response)["reply"] == "[ ] #1 Vérifier"
        finally:
            client.close()
            server.shutdown()
            worker.join()
