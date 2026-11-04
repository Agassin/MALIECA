import pytest

from app.ai.models.config import TransformerConfig


def test_transformer_config_calcule_la_dimension_des_tetes():
    config = TransformerConfig(
        vocab_size=512,
        d_model=128,
        num_layers=4,
        num_heads=8,
        max_sequence_length=256,
        feed_forward_dim=512,
        dropout=0.1,
    )

    assert config.head_dim == 16


@pytest.mark.parametrize(
    "field,value",
    [
        ("vocab_size", 256),
        ("d_model", 0),
        ("num_layers", 0),
        ("num_heads", 0),
        ("max_sequence_length", 0),
        ("feed_forward_dim", 0),
    ],
)
def test_transformer_config_refuse_les_dimensions_invalides(field, value):
    values = {
        "vocab_size": 512,
        "d_model": 128,
        "num_layers": 4,
        "num_heads": 8,
        "max_sequence_length": 256,
        "feed_forward_dim": 512,
    }
    values[field] = value

    with pytest.raises(ValueError):
        TransformerConfig(**values)


def test_transformer_config_refuse_un_nombre_de_tetes_incompatible():
    with pytest.raises(ValueError, match="divisible"):
        TransformerConfig(
            vocab_size=512,
            d_model=127,
            num_layers=4,
            num_heads=8,
            max_sequence_length=256,
            feed_forward_dim=512,
        )


@pytest.mark.parametrize("dropout", [-0.1, 1.0, 2.0])
def test_transformer_config_refuse_un_dropout_hors_limites(dropout):
    with pytest.raises(ValueError, match="dropout"):
        TransformerConfig(
            vocab_size=512,
            d_model=128,
            num_layers=4,
            num_heads=8,
            max_sequence_length=256,
            feed_forward_dim=512,
            dropout=dropout,
        )


def test_transformer_config_refuse_un_booleen_comme_dimension():
    with pytest.raises(ValueError, match="d_model"):
        TransformerConfig(
            vocab_size=512,
            d_model=True,
            num_layers=4,
            num_heads=8,
            max_sequence_length=256,
            feed_forward_dim=512,
        )
