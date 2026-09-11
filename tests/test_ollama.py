import json
from unittest.mock import patch
from urllib.error import URLError

from app.ai.base import AIMessage
from app.ai.providers.ollama import OllamaModel


class FakeResponse:
    def __init__(self, content: dict[str, object]) -> None:
        self.data = json.dumps(content).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self) -> bytes:
        return self.data


def test_ollama_envoie_les_messages_et_recupere_la_reponse():
    response = FakeResponse(
        {
            "model": "llama3.2",
            "message": {"role": "assistant", "content": "Bonjour !"},
        }
    )

    with patch(
        "app.ai.providers.ollama.request.urlopen",
        return_value=response,
    ) as urlopen:
        model = OllamaModel()
        result = model.generate([AIMessage(role="user", content="Bonjour")])

    assert result.content == "Bonjour !"
    assert result.metadata["model"] == "llama3.2"
    urlopen.assert_called_once()


def test_ollama_signale_quand_le_service_est_inaccessible():
    with patch(
        "app.ai.providers.ollama.request.urlopen",
        side_effect=URLError("connexion refusée"),
    ):
        model = OllamaModel()

        try:
            model.generate([AIMessage(role="user", content="Bonjour")])
            assert False
        except RuntimeError as error:
            assert "Impossible de contacter Ollama" in str(error)
