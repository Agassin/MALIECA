"""Moteur qui orchestre le fonctionnement de M.A.L.I.E.C.A."""

from app.ai.base import AIToolDefinition, AIModel
from app.core.models import ConversationContext
from app.tools.base import ToolResult
from app.tools.builtin.clock import ClockTool
from app.tools.registry import ToolRegistry


class Runtime:
    """Gère le contexte, les outils et le modèle IA."""

    def __init__(
        self,
        model: AIModel | None = None,
        tool_registry: ToolRegistry | None = None,
        max_tool_iterations: int = 8,
    ) -> None:
        self.model = model
        self.context = ConversationContext()
        self.tool_registry = tool_registry or ToolRegistry()
        self.max_tool_iterations = max_tool_iterations

        # On ajoute les outils de base quand aucun registre n'est fourni.
        if tool_registry is None:
            self.tool_registry.register(ClockTool())

    def respond(self, message: str, assistant_name: str) -> str:
        """Traite un message et renvoie la réponse de M.A.L.I.E.C.A."""
        cleaned_message = message.strip()
        if not cleaned_message:
            return "Je n'ai pas reçu de demande."

        self.context.add_user_message(cleaned_message)

        # Tant qu'aucun vrai modèle n'est branché, on garde le comportement actuel.
        if self.model is None:
            response = f"{assistant_name} a reçu : {cleaned_message}"
            self.context.add_assistant_message(response)
            return response

        for _ in range(self.max_tool_iterations):
            response = self.model.generate(
                self.context.messages,
                tools=self._get_tool_definitions(),
            )

            if not response.tool_calls:
                self.context.add_assistant_message(response.content)
                return response.content

            self.context.add_assistant_message(
                response.content,
                tool_calls=response.tool_calls,
            )

            for tool_call in response.tool_calls:
                result = self.execute_tool(tool_call.name, tool_call.arguments)
                self.context.add_tool_message(
                    self._format_tool_result(result),
                    tool_call.id,
                )

        raise RuntimeError(
            "La boucle agentique a atteint sa limite d'itérations."
        )

    def execute_tool(
        self,
        name: str,
        arguments: dict[str, object],
    ) -> ToolResult:
        """Exécute un outil enregistré."""
        tool = self.tool_registry.get(name)
        return tool.execute(arguments)

    def _get_tool_definitions(self) -> list[AIToolDefinition]:
        """Transforme les outils disponibles en contrat pour le modèle."""
        return [
            AIToolDefinition(
                name=tool.name,
                description=tool.description,
                risk_level=int(tool.risk_level),
            )
            for tool in self.tool_registry.list_tools()
        ]

    @staticmethod
    def _format_tool_result(result: ToolResult) -> str:
        """Transforme un résultat d'outil en message compréhensible par le modèle."""
        if result.success:
            return str(result.output)
        return f"Erreur de l'outil : {result.error or 'erreur inconnue'}"
