from datetime import datetime

from app.tools.base import ToolRisk
from app.tools.builtin.clock import ClockTool


def test_clock_est_un_outil_lecture_seule():
    tool = ClockTool()

    assert tool.name == "get_current_time"
    assert tool.risk_level == ToolRisk.READ_ONLY


def test_clock_renvoie_la_date_et_l_heure():
    tool = ClockTool()
    result = tool.execute({})

    assert result.success is True
    assert isinstance(result.output, str)
    assert datetime.now().astimezone().strftime("%d/%m/%Y") in result.output
