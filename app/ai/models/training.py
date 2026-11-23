"""Données et entraînement supervisé du prototype MALIECA-LLM."""

import hashlib
import json
import random
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

import torch
from torch import Tensor, nn

from app.ai.base import AIMessage
from app.ai.models.chat_format import ChatFormat
from app.ai.models.config import TransformerConfig
from app.ai.models.transformer import Transformer
from app.ai.providers.malieca import CHECKPOINT_FORMAT
from app.ai.tokenizers.bpe import BytePairTokenizer

Example = tuple[str, str]
EncodedExample = tuple[list[int], list[int]]
IGNORE = -100


def read_corpus(path: Path) -> tuple[list[Example], str]:
    """Lit des exemples JSONL et identifie précisément leur version par SHA-256."""
    raw = path.read_bytes()
    examples: list[Example] = []
    for index, line in enumerate(raw.decode("utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            prompt, reply = entry["user"], entry["assistant"]
            if not all(isinstance(text, str) and text.strip() for text in (prompt, reply)):
                raise ValueError
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"{path}:{index} — champs « user » et « assistant » requis.") from error
        examples.append((prompt.strip(), reply.strip()))
    if not examples:
        raise ValueError(f"{path} ne contient aucun exemple.")
    return examples, hashlib.sha256(raw).hexdigest()


def unique_prompts(examples: list[Example]) -> set[str]:
    prompts = {" ".join(prompt.casefold().split()) for prompt, _ in examples}
    if len(prompts) != len(examples):
        raise ValueError("Un corpus contient des demandes en double.")
    return prompts


def encode_examples(
    examples: list[Example], chat_format: ChatFormat, window: int
) -> list[EncodedExample]:
    encoded: list[EncodedExample] = []
    for index, (prompt, reply) in enumerate(examples, start=1):
        prefix = chat_format.prompt([AIMessage("user", prompt)])
        completion = chat_format.completion(reply)
        if len(prefix) + len(completion) - 1 > window:
            raise ValueError(f"L'exemple {index} dépasse la fenêtre de {window} tokens.")
        encoded.append((prefix + completion[:-1], [IGNORE] * (len(prefix) - 1) + completion))
    return encoded


def batch(examples: list[EncodedExample]) -> tuple[Tensor, Tensor]:
    length = max(len(tokens) for tokens, _ in examples)
    inputs = torch.tensor([tokens + [0] * (length - len(tokens)) for tokens, _ in examples])
    targets = torch.tensor(
        [targets + [IGNORE] * (length - len(targets)) for _, targets in examples]
    )
    return inputs, targets


@torch.inference_mode()
def evaluate(model: Transformer, examples: list[EncodedExample], batch_size: int) -> float:
    model.eval()
    criterion = nn.CrossEntropyLoss(ignore_index=IGNORE, reduction="sum")
    loss = 0.0
    token_count = 0
    for start in range(0, len(examples), batch_size):
        inputs, targets = batch(examples[start:start + batch_size])
        loss += criterion(model(inputs).flatten(0, 1), targets.flatten()).item()
        token_count += int((targets != IGNORE).sum())
    return loss / token_count


def fit(
    train: list[Example],
    validation: list[Example],
    *,
    steps: int,
    seed: int,
    batch_size: int = 8,
    window: int = 192,
) -> tuple[Transformer, BytePairTokenizer, dict[str, float]]:
    if min(steps, batch_size, window) < 1 or not train or not validation:
        raise ValueError("Entraînement et validation requièrent des exemples et des tailles positives.")
    if unique_prompts(train) & unique_prompts(validation):
        raise ValueError("Des demandes sont communes à l'entraînement et à la validation.")

    torch.manual_seed(seed)
    rng = random.Random(seed)
    tokenizer = BytePairTokenizer.train([text for example in train for text in example])
    chat_format = ChatFormat(tokenizer)
    config = TransformerConfig(chat_format.size, 48, 2, 4, window, 128)
    model = Transformer(config)
    train_encoded = encode_examples(train, chat_format, window)
    validation_encoded = encode_examples(validation, chat_format, window)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.002)
    criterion = nn.CrossEntropyLoss(ignore_index=IGNORE)

    initial = evaluate(model, validation_encoded, batch_size)
    model.train()
    for _ in range(steps):
        selected = rng.sample(train_encoded, k=min(len(train_encoded), batch_size))
        inputs, targets = batch(selected)
        optimizer.zero_grad(set_to_none=True)
        loss = criterion(model(inputs).flatten(0, 1), targets.flatten())
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

    metrics = {
        "validation_initial": initial,
        "validation_finale": evaluate(model, validation_encoded, batch_size),
        "entrainement_final": evaluate(model, train_encoded, batch_size),
    }
    return model, tokenizer, metrics


def save_checkpoint(
    path: Path, model: Transformer, tokenizer: BytePairTokenizer, run: dict[str, object]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=path.parent, prefix=".checkpoint-") as directory:
        temporary = Path(directory) / "model.pt"
        torch.save(
            {
                "format": CHECKPOINT_FORMAT,
                "config": asdict(model.config),
                "merges": [[left.hex(), right.hex()] for left, right in tokenizer.merges],
                "weights": model.state_dict(),
                "run": run,
            },
            temporary,
        )
        temporary.replace(path)
