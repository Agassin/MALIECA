from unittest.mock import patch

from app.main import main


def test_main_runs(capsys):
    with patch("builtins.input", return_value="quit"):
        main()

    output = capsys.readouterr().out
    assert "M.A.L.I.E.C.A." in output
    assert "Arrêt de M.A.L.I.E.C.A." in output
