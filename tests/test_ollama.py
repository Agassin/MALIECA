import json
from unittest.mock import patch
from urllib.error import URLError

import pytest

from app.ai.base import AIToolDefinition, AIMessage, ToolCall
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
            "model": "qwen3",
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
    assert result.metadata["model"] == "qwen3"
    urlopen.assert_called_once()


def test_ollama_convertit_les_appels_d_outils():
    response = FakeResponse(
        {
            "model": "qwen3",
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "get_current_time",
                            "arguments": {},
                        },
                    }
                ],
            },
        }
    )
    tool = AIToolDefinition(
        name="get_current_time",
        description="Donne la date et l'heure actuelles.",
        risk_level=0,
    )

    with patch(
        "app.ai.providers.ollama.request.urlopen",
        return_value=response,
    ) as urlopen:
        model = OllamaModel()
        result = model.generate(
            [AIMessage(role="user", content="Quelle heure est-il ?")],
            tools=[tool],
        )

    assert result.content == ""
    assert result.tool_calls == (
        ToolCall(
            id="ollama-call-0",
            name="get_current_time",
            arguments={},
        ),
    )

    payload = json.loads(urlopen.call_args.args[0].data.decode("utf-8"))
    assert payload["model"] == "qwen3"
    assert payload["tools"][0]["function"]["name"] == "get_current_time"


def test_ollama_serialise_le_resultat_d_un_outil():
    response = FakeResponse(
        {
            "model": "qwen3",
            "message": {"role": "assistant", "content": "Il est 18h."},
        }
    )
    messages = [
        AIMessage(role="user", content="Quelle heure est-il ?"),
        AIMessage(
            role="assistant",
            content="",
            tool_calls=(ToolCall("call-1", "get_current_time"),),
        ),
        AIMessage(
            role="tool",
            content="Il est 18h.",
            tool_call_id="call-1",
            tool_name="get_current_time",
        ),
    ]

    with patch(
        "app.ai.providers.ollama.request.urlopen",
        return_value=response,
    ) as urlopen:
        OllamaModel().generate(messages)

    payload = json.loads(urlopen.call_args.args[0].data.decode("utf-8"))
    assert payload["messages"][1]["tool_calls"][0]["function"]["name"] == (
        "get_current_time"
    )
    assert payload["messages"][2]["tool_name"] == "get_current_time"


def test_ollama_signale_quand_le_service_est_inaccessible():
    with patch(
        "app.ai.providers.ollama.request.urlopen",
        side_effect=URLError("connexion refusée"),
    ):
        model = OllamaModel()

        with pytest.raises(RuntimeError, match="Impossible de contacter Ollama"):
            model.generate([AIMessage(role="user", content="Bonjour")])
