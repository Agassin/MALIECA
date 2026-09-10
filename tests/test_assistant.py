from app.core.assistant import Assistant


def test_assistant_responds_to_message():
    assistant = Assistant()
    assert "Bonjour" in assistant.respond("Bonjour")


def test_assistant_handles_empty_message():
    assistant = Assistant()
    assert assistant.respond("   ") == "Je n'ai pas reçu de demande."
