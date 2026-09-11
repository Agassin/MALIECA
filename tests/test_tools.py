from app.tools.base import Tool, ToolResult, ToolRisk
from app.tools.registry import ToolRegistry


class FakeTool(Tool):
    name = "fake"
    description = "Outil utilisé pour les tests."
    risk_level = ToolRisk.READ_ONLY

    def execute(self, arguments: dict[str, object]) -> ToolResult:
        return ToolResult(success=True, output=arguments)


def test_registry_enregistre_et_retrouve_un_outil():
    registry = ToolRegistry()
    tool = FakeTool()

    registry.register(tool)

    assert registry.get("fake") is tool
    assert registry.list_tools() == [tool]


def test_registry_refuse_un_doublon():
    registry = ToolRegistry()
    registry.register(FakeTool())

    try:
        registry.register(FakeTool())
        assert False
    except ValueError as error:
        assert "existe déjà" in str(error)


def test_outil_retourne_un_resultat():
    tool = FakeTool()

    result = tool.execute({"message": "Bonjour"})

    assert result.success is True
    assert result.output == {"message": "Bonjour"}
