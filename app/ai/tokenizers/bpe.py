"""Prototype de tokenizer BPE au niveau des octets."""

import json
from pathlib import Path


class BytePairTokenizer:
    """Tokenizer BPE minimal, déterministe et sans dépendance externe."""

    FORMAT = "malieca-byte-bpe-v1"
    BASE_VOCAB_SIZE = 256

    def __init__(self, merges: list[tuple[bytes, bytes]] | None = None) -> None:
        self.merges = list(merges or [])
        self.vocabulary: dict[bytes, int] = {
            bytes([value]): value for value in range(self.BASE_VOCAB_SIZE)
        }
        for left, right in self.merges:
            token = left + right
            if token not in self.vocabulary:
                self.vocabulary[token] = len(self.vocabulary)

    @classmethod
    def train(
        cls,
        texts: list[str],
        vocab_size: int = 512,
        min_frequency: int = 2,
    ) -> "BytePairTokenizer":
        """Apprend les fusions les plus fréquentes sur un petit corpus."""
        if vocab_size < cls.BASE_VOCAB_SIZE:
            raise ValueError("La taille du vocabulaire doit être au moins 256.")
        if min_frequency < 1:
            raise ValueError("La fréquence minimale doit être positive.")

        sequences = [[bytes([value]) for value in text.encode("utf-8")] for text in texts]
        merges: list[tuple[bytes, bytes]] = []
        vocabulary = {bytes([value]) for value in range(cls.BASE_VOCAB_SIZE)}

        while len(vocabulary) < vocab_size:
            frequencies: dict[tuple[bytes, bytes], int] = {}
            for sequence in sequences:
                for index in range(len(sequence) - 1):
                    pair = (sequence[index], sequence[index + 1])
                    frequencies[pair] = frequencies.get(pair, 0) + 1

            if not frequencies:
                break

            pair, frequency = max(
                frequencies.items(),
                key=lambda item: (item[1], item[0]),
            )
            if frequency < min_frequency:
                break

            left, right = pair
            merged = left + right
            merges.append(pair)
            vocabulary.add(merged)

            updated_sequences: list[list[bytes]] = []
            for sequence in sequences:
                updated: list[bytes] = []
                index = 0
                while index < len(sequence):
                    if (
                        index + 1 < len(units)
                        and units[index] == left
                        and units[index + 1] == right
                    ):
                        updated.append(merged)
                        index += 2
                    else:
                        updated.append(sequence[index])
                        index += 1
                updated_sequences.append(updated)

            sequences = updated_sequences

        return cls(merges)

    def encode(self, text: str) -> list[int]:
        """Convertit un texte en identifiants de tokens."""
        units = [bytes([value]) for value in text.encode("utf-8")]
        for left, right in self.merges:
            merged = left + right
            updated: list[bytes] = []
            index = 0
            while index < len(units):
                if (
                    index + 1 < len(units)
                    and sequence[index] == left
                    and sequence[index + 1] == right
                ):
                    updated.append(merged)
                    index += 2
                else:
                    updated.append(units[index])
                    index += 1
            units = updated
        return [self.vocabulary[unit] for unit in units]

    def decode(self, token_ids: list[int]) -> str:
        """Reconstruit le texte à partir des identifiants de tokens."""
        reverse_vocabulary = {
            token_id: token for token, token_id in self.vocabulary.items()
        }
        try:
            raw_text = b"".join(reverse_vocabulary[token_id] for token_id in token_ids)
        except KeyError as error:
            raise ValueError(f"Identifiant de token inconnu : {error.args[0]}") from error
        return raw_text.decode("utf-8")

    def save(self, path: str | Path) -> None:
        """Enregistre les fusions apprises au format JSON."""
        data = {
            "format": self.FORMAT,
            "merges": [[left.hex(), right.hex()] for left, right in self.merges],
        }
        Path(path).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "BytePairTokenizer":
        """Recharge un tokenizer enregistré."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("format") != cls.FORMAT:
            raise ValueError("Format de tokenizer non reconnu.")
        try:
            merges = [
                (bytes.fromhex(left), bytes.fromhex(right))
                for left, right in data["merges"]
            ]
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Fichier de tokenizer invalide.") from error
        return cls(merges)
