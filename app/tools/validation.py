"""Validation stricte des arguments reçus par les outils."""


_JSON_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
}


def validate_arguments(arguments: object, schema: dict[str, object]) -> None:
    """Valide un objet d'arguments selon le sous-ensemble JSON Schema utilisé."""
    _validate_value(arguments, schema, "arguments")


def _validate_value(value: object, schema: dict[str, object], path: str) -> None:
    expected_type = schema.get("type")
    if expected_type == "null":
        if value is not None:
            raise ValueError(f"{path} doit être null.")
    elif expected_type in _JSON_TYPES:
        python_type = _JSON_TYPES[expected_type]
        if expected_type == "integer":
            valid_type = isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == "number":
            valid_type = isinstance(value, (int, float)) and not isinstance(value, bool)
        else:
            valid_type = isinstance(value, python_type)
        if not valid_type:
            raise ValueError(f"{path} doit être de type {expected_type}.")
    elif expected_type is not None:
        raise ValueError(f"Type de schéma non pris en charge : {expected_type}.")

    enum_values = schema.get("enum")
    if isinstance(enum_values, list) and value not in enum_values:
        raise ValueError(f"{path} doit appartenir aux valeurs autorisées.")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        if not isinstance(properties, dict) or not isinstance(required, list):
            raise TypeError(f"Schéma d'objet invalide pour {path}.")

        for name in required:
            if not isinstance(name, str):
                raise TypeError(f"Schéma required invalide pour {path}.")
            if name not in value:
                raise ValueError(f"{path}.{name} est obligatoire.")

        additional = schema.get("additionalProperties", False)
        for name, item in value.items():
            if name in properties:
                property_schema = properties[name]
                if not isinstance(property_schema, dict):
                    raise ValueError(f"Schéma invalide pour {path}.{name}.")
                _validate_value(item, property_schema, f"{path}.{name}")
            elif additional is False:
                raise ValueError(f"{path}.{name} n'est pas autorisé.")
            elif isinstance(additional, dict):
                _validate_value(item, additional, f"{path}.{name}")

    if isinstance(value, list):
        items_schema = schema.get("items")
        if isinstance(items_schema, dict):
            for index, item in enumerate(value):
                _validate_value(item, items_schema, f"{path}[{index}]")

    if isinstance(value, (str, list)):
        min_key, max_key = (
            ("minLength", "maxLength") if isinstance(value, str)
            else ("minItems", "maxItems")
        )
        minimum = schema.get(min_key)
        maximum = schema.get(max_key)
        if isinstance(minimum, int) and len(value) < minimum:
            raise ValueError(f"{path} est trop court.")
        if isinstance(maximum, int) and len(value) > maximum:
            raise ValueError(f"{path} est trop long.")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, (int, float)) and value < minimum:
            raise ValueError(f"{path} est inférieur au minimum autorisé.")
        if isinstance(maximum, (int, float)) and value > maximum:
            raise ValueError(f"{path} dépasse le maximum autorisé.")
