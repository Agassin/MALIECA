import pytest

from app.tools.validation import validate_arguments


def test_validation_accepte_les_arguments_conformes():
    schema = {
        "type": "object",
        "properties": {
            "city": {"type": "string", "minLength": 2},
            "days": {"type": "integer", "minimum": 1, "maximum": 7},
        },
        "required": ["city"],
    }

    validate_arguments({"city": "Vannes", "days": 3}, schema)


@pytest.mark.parametrize(
    "arguments",
    [
        {"city": "Vannes", "days": "trois"},
        {"city": "Vannes", "days": True},
        {"city": "Vannes", "days": 0},
        {"city": "Vannes", "days": 8},
        {"city": "Vannes", "unknown": "value"},
        {"days": 3},
    ],
)
def test_validation_refuse_les_arguments_invalides(arguments):
    schema = {
        "type": "object",
        "properties": {
            "city": {"type": "string", "minLength": 2},
            "days": {"type": "integer", "minimum": 1, "maximum": 7},
        },
        "required": ["city"],
    }

    with pytest.raises(ValueError):
        validate_arguments(arguments, schema)


def test_validation_refuse_un_tableau_avec_un_element_invalide():
    schema = {
        "type": "object",
        "properties": {
            "values": {"type": "array", "items": {"type": "integer"}},
        },
    }

    with pytest.raises(ValueError, match="type integer"):
        validate_arguments({"values": [1, "deux"]}, schema)


def test_validation_refuse_les_arguments_qui_ne_sont_pas_un_objet():
    with pytest.raises(ValueError, match="type object"):
        validate_arguments(["pas", "un", "objet"], {"type": "object"})
