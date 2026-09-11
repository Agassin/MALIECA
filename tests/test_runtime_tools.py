from app.core.runtime import Runtime


def test_runtime_execute_un_outil():
    runtime = Runtime()

    result = runtime.execute_tool("get_current_time", {})

    assert result.success is True
    assert "Nous sommes le" in result.output
