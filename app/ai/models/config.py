"""Configuration validée pour le futur Transformer décodeur."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TransformerConfig:
    """Décrit les dimensions d'un Transformer sans imposer de backend."""

    vocab_size: int
    d_model: int
    num_layers: int
    num_heads: int
    max_sequence_length: int
    feed_forward_dim: int
    dropout: float = 0.0

    def __post_init__(self) -> None:
        """Vérifie les contraintes structurelles avant de construire le modèle."""
        dimensions = {
            "vocab_size": self.vocab_size,
            "d_model": self.d_model,
            "num_layers": self.num_layers,
            "num_heads": self.num_heads,
            "max_sequence_length": self.max_sequence_length,
            "feed_forward_dim": self.feed_forward_dim,
        }
        for name, value in dimensions.items():
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} doit être un entier strictement positif.")

        if self.vocab_size <= 256:
            raise ValueError("vocab_size doit réserver des identifiants au-delà des 256 octets.")

        if self.d_model % self.num_heads != 0:
            raise ValueError("d_model doit être divisible par num_heads.")

        if not isinstance(self.dropout, (int, float)) or isinstance(self.dropout, bool):
            raise ValueError("dropout doit être un nombre compris entre 0 et 1.")
        if not 0 <= self.dropout < 1:
            raise ValueError("dropout doit être compris entre 0 inclus et 1 exclu.")

    @property
    def head_dim(self) -> int:
        """Retourne la dimension de chaque tête d'attention."""
        return self.d_model // self.num_heads
