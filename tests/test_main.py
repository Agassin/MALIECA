from app.main import main


def test_main_runs(capsys):
    main()
    output = capsys.readouterr().out
    assert "M.A.L.I.E.C.A." in output
