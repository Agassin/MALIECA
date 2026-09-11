from app.ai.base import AIMessage, AIModel, AIResponse
from app.core.assistant import Assistant


class FakeModel(AIModel):
    def generate(self, messages: list[AIMessage]) -> AIResponse:
        return AIResponse(content=f"Réponse au dernier message : {messages[-1].content}")


def test_assistant_uses_model_through_runtime():
    assistant = Assistant(model=FakeModel())

    assert assistant.respond("Bonjour") == "Réponse au dernier message : Bonjour"
    assert len(assistant.runtime.context.messages) == 2


def test_runtime_keeps_previous_context():
    assistant = Assistant(model=FakeModel())

    assistant.respond("Premier message")
    assistant.respond("Deuxième message")

    messages = assistant.runtime.context.messages
    assert len(messages) == 4
    assert messages[0].content == "Premier message"
    assert messages[2].content == "Deuxième message"
