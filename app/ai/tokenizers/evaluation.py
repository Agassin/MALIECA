"""Mesures simples pour évaluer un tokenizer sur un corpus."""

from dataclasses import dataclass

from app.ai.tokenizers.bpe import BytePairTokenizer


@dataclass(frozen=True)
class TokenizerMetrics:
    """Mesures agrégées d'un tokenizer sur un corpus."""

    text_count: int
    byte_count: int
    token_count: int
    vocabulary_size: int
    merge_count: int
    bytes_per_token: float
    compression_ratio: float
    round_trip_ok: bool


def evaluate_tokenizer(
    tokenizer: BytePairTokenizer,
    texts: list[str],
) -> TokenizerMetrics:
    """Mesure le nombre de tokens et vérifie la réversibilité du corpus."""
    if not texts:
        raise ValueError("Le corpus d'évaluation ne peut pas être vide.")

    byte_count = 0
    token_count = 0
    round_trip_ok = True

    for text in texts:
        encoded = tokenizer.encode(text)
        byte_count += len(text.encode("utf-8"))
        token_count += len(encoded)
        if tokenizer.decode(encoded) != text:
            round_trip_ok = False

    bytes_per_token = byte_count / token_count if token_count else 0.0
    compression_ratio = byte_count / token_count if token_count else 0.0

    return TokenizerMetrics(
        text_count=len(texts),
        byte_count=byte_count,
        token_count=token_count,
        vocabulary_size=len(tokenizer.vocabulary),
        merge_count=len(tokenizer.merges),
        bytes_per_token=bytes_per_token,
        compression_ratio=compression_ratio,
        round_trip_ok=round_trip_ok,
    )
