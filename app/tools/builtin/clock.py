"""Outil qui donne la date et l'heure actuelles."""

from datetime import datetime
from typing import Any

from app.tools.base import Tool, ToolResult, ToolRisk


class ClockTool(Tool):
    """Donne la date et l'heure actuelles."""

    name = "get_current_time"
    description = "Donne la date et l'heure actuelles."
    risk_level = ToolRisk.READ_ONLY

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        """Renvoie la date et l'heure actuelles."""
        now = datetime.now().astimezone()
        output = now.strftime("Nous sommes le %d/%m/%Y et il est %H:%M:%S.")
        return ToolResult(success=True, output=output)
