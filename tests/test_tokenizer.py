from pathlib import Path

import pytest

from app.ai.tokenizers.bpe import BytePairTokenizer


def test_bpe_encode_decode_preserve_le_texte_francais():
    tokenizer = BytePairTokenizer.train(
        ["bonjour bonjour", "bonjour le monde", "M.A.L.I.E.C.A."],
        vocab_size=300,
    )
    text = "Bonjour, M.A.L.I.E.C.A. — déjà prêt ?"

    assert tokenizer.decode(tokenizer.encode(text)) == text


def test_bpe_apprend_des_fusions_reproductibles():
    corpus = ["abababab", "abab", "abab"]
    first = BytePairTokenizer.train(corpus, vocab_size=260)
    second = BytePairTokenizer.train(corpus, vocab_size=260)

    assert first.merges == second.merges
    assert len(first.vocabulary) > BytePairTokenizer.BASE_VOCAB_SIZE


def test_bpe_peut_etre_enregistre_et_recharge(tmp_path: Path):
    tokenizer = BytePairTokenizer.train(["un petit corpus", "un corpus simple"])
    destination = tmp_path / "tokenizer.json"
    tokenizer.save(destination)

    loaded = BytePairTokenizer.load(destination)

    assert loaded.merges == tokenizer.merges
    assert loaded.decode(loaded.encode("MALIECA")) == "MALIECA"


def test_bpe_refuse_une_taille_de_vocabulaire_invalide():
    with pytest.raises(ValueError, match="au moins 256"):
        BytePairTokenizer.train(["texte"], vocab_size=128)


def test_bpe_refuse_un_identifiant_inconnu():
    tokenizer = BytePairTokenizer()

    with pytest.raises(ValueError, match="Identifiant de token inconnu"):
        tokenizer.decode([999])
