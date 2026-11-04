from app.ai.tokenizers.bpe import BytePairTokenizer
from app.ai.tokenizers.evaluation import evaluate_tokenizer


def test_evaluation_calcule_les_mesures_et_verifie_le_round_trip():
    texts = ["bonjour", "MALIECA", "déjà prêt"]
    tokenizer = BytePairTokenizer.train(texts * 3, vocab_size=280)

    metrics = evaluate_tokenizer(tokenizer, texts)

    assert metrics.text_count == len(texts)
    assert metrics.byte_count == sum(len(text.encode("utf-8")) for text in texts)
    assert metrics.token_count > 0
    assert metrics.vocabulary_size == len(tokenizer.vocabulary)
    assert metrics.merge_count == len(tokenizer.merges)
    assert metrics.bytes_per_token > 0
    assert metrics.compression_ratio == metrics.bytes_per_token
    assert metrics.round_trip_ok is True


def test_evaluation_accepte_un_corpus_de_textes_vides():
    metrics = evaluate_tokenizer(BytePairTokenizer(), ["", ""])

    assert metrics.byte_count == 0
    assert metrics.token_count == 0
    assert metrics.bytes_per_token == 0
    assert metrics.round_trip_ok is True


def test_evaluation_refuse_un_corpus_vide():
    try:
        evaluate_tokenizer(BytePairTokenizer(), [])
        assert False
    except ValueError as error:
        assert "ne peut pas être vide" in str(error)
