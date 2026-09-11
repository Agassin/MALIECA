from app.ai.base import AIMessage, AIModel, AIResponse, ToolCall
from app.core.assistant import Assistant
from app.tools.base import Tool, ToolResult, ToolRisk
from app.tools.registry import ToolRegistry


class FakeModel(AIModel):
    def generate(self, messages: list[AIMessage], tools=None) -> AIResponse:
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


class FakeRuntimeTool(Tool):
    name = "fake"
    description = "Outil utilisé pour les tests du Runtime."
    risk_level = ToolRisk.READ_ONLY

    def execute(self, arguments: dict[str, object]) -> ToolResult:
        return ToolResult(success=True, output=arguments)


class AgenticFakeModel(AIModel):
    def __init__(self) -> None:
        self.calls = 0
        self.received_tools = []

    def generate(self, messages: list[AIMessage], tools=None) -> AIResponse:
        self.calls += 1
        self.received_tools = tools or []

        if self.calls == 1:
            return AIResponse(
                content="Je vais utiliser l'outil.",
                tool_calls=(
                    ToolCall(
                        id="call-1",
                        name="fake",
                        arguments={"message": "Bonjour"},
                    ),
                ),
            )

        return AIResponse(content=f"Résultat reçu : {messages[-1].content}")


def test_runtime_execute_la_boucle_agentique():
    model = AgenticFakeModel()
    registry = ToolRegistry()
    registry.register(FakeRuntimeTool())
    assistant = Assistant(model=model)
    assistant.runtime.tool_registry = registry

    result = assistant.respond("Utilise l'outil")

    assert result == "Résultat reçu : {'message': 'Bonjour'}"
    assert model.calls == 2
    assert len(model.received_tools) == 1
    assert model.received_tools[0].name == "fake"
    assert [message.role for message in assistant.runtime.context.messages] == [
        "user",
        "assistant",
        "tool",
        "assistant",
    ]


def test_runtime_arrete_une_boucle_agentique_infinie():
    class LoopingModel(AIModel):
        def generate(self, messages: list[AIMessage], tools=None) -> AIResponse:
            return AIResponse(
                content="Encore un outil.",
                tool_calls=(ToolCall(id="loop", name="fake"),),
            )

    registry = ToolRegistry()
    registry.register(FakeRuntimeTool())
    assistant = Assistant(model=LoopingModel())
    assistant.runtime.tool_registry = registry
    assistant.runtime.max_tool_iterations = 2

    try:
        assistant.respond("Boucle")
        assert False
    except RuntimeError as error:
        assert "limite d'itérations" in str(error)
