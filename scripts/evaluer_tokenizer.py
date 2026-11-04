"""Évalue le prototype BPE sur un corpus de démonstration créé pour MALIECA."""

from app.ai.tokenizers.bpe import BytePairTokenizer


CORPUS = [
    "Bonjour, je suis MALIECA, ton assistant personnel.",
    "Je peux analyser une demande, préparer un plan et utiliser des outils autorisés.",
    "La sécurité reste sous le contrôle du Runtime.",
    "Un modèle de langage prédit le prochain token à partir du contexte.",
    "Les données d'entraînement doivent avoir une provenance et une licence documentées.",
    "def respond(message: str) -> str:",
    "    return assistant.respond(message)",
    "class ConversationContext:",
    "    def add_user_message(self, content: str) -> None:",
    "MALIECA utilise Python, des tests automatisés et Git.",
] * 4


def main() -> None:
    """Entraîne le tokenizer de démonstration puis affiche ses mesures."""
    from app.ai.tokenizers.evaluation import evaluate_tokenizer

    tokenizer = BytePairTokenizer.train(
        CORPUS,
        vocab_size=512,
        min_frequency=2,
    )
    metrics = evaluate_tokenizer(tokenizer, CORPUS)

    print("Évaluation du tokenizer BPE de MALIECA")
    print("--------------------------------------")
    print(f"Textes évalués       : {metrics.text_count}")
    print(f"Octets UTF-8         : {metrics.byte_count}")
    print(f"Tokens produits      : {metrics.token_count}")
    print(f"Taille du vocabulaire: {metrics.vocabulary_size}")
    print(f"Fusions apprises     : {metrics.merge_count}")
    print(f"Octets par token     : {metrics.bytes_per_token:.3f}")
    print(f"Ratio octets/tokens  : {metrics.compression_ratio:.3f}")
    print(f"Réversibilité        : {'OK' if metrics.round_trip_ok else 'ÉCHEC'}")
    print()
    print("Note : corpus synthétique de démonstration, pas un benchmark représentatif.")


if __name__ == "__main__":
    main()
