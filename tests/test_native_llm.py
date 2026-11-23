from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

from app.ai.base import AIMessage
from app.ai.models.config import TransformerConfig
from app.ai.models.training import fit, read_corpus, save_checkpoint
from app.ai.models.transformer import Transformer
from app.ai.providers.malieca import MaliecaModel

DEMO = Path(__file__).resolve().parents[1] / "data" / "demo"


def test_transformer_respects_causal_mask():
    torch.manual_seed(5)
    model = Transformer(TransformerConfig(270, 24, 2, 4, 8, 32)).eval()
    tokens = torch.tensor([[1, 2, 3], [1, 2, 4]])
    with torch.inference_mode():
        logits = model(tokens)

    assert logits.shape == (2, 3, 270)
    torch.testing.assert_close(logits[0, :2], logits[1, :2])
    assert not torch.allclose(logits[0, 2], logits[1, 2])


def test_training_checkpoint_and_native_inference(tmp_path):
    torch.set_num_threads(1)
    train, train_hash = read_corpus(DEMO / "train.jsonl")
    validation, validation_hash = read_corpus(DEMO / "validation.jsonl")
    model, tokenizer, metrics = fit(train, validation, steps=160, seed=42)

    assert train_hash != validation_hash
    assert metrics["validation_finale"] < metrics["validation_initial"]
    path = tmp_path / "demo.pt"
    save_checkpoint(path, model, tokenizer, {"metrics": metrics})
    provider = MaliecaModel.load(path)
    for key, weight in model.state_dict().items():
        assert torch.equal(weight, provider.transformer.state_dict()[key])

    result = provider.generate([AIMessage("user", "Bonjour")])
    assert result.content.startswith("Bonjour")


def test_training_rejects_cross_split_prompt_leakage():
    with pytest.raises(ValueError, match="communes"):
        fit([(" Salut ", "Bonjour")], [("salut", "Coucou")], steps=1, seed=42)
