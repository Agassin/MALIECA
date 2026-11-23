"""Entraîne un petit MALIECA-LLM sur CPU et enregistre le checkpoint."""

import json
import platform
from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter

import torch

from app.ai.models.training import fit, read_corpus, save_checkpoint
from app.ai.tokenizers.evaluation import evaluate_tokenizer

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=ROOT / "data/demo/train.jsonl")
    parser.add_argument("--validation", type=Path, default=ROOT / "data/demo/validation.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / ".data/malieca-demo.pt")
    parser.add_argument("--steps", type=int, default=160)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args()
    if args.threads < 1:
        parser.error("--threads doit être strictement positif.")

    torch.set_num_threads(args.threads)
    start = perf_counter()
    try:
        train, train_hash = read_corpus(args.train)
        validation, validation_hash = read_corpus(args.validation)
        model, tokenizer, metrics = fit(train, validation, steps=args.steps, seed=args.seed)
        tokenizer_metrics = evaluate_tokenizer(
            tokenizer, [text for example in validation for text in example]
        )
        report = {
            "seed": args.seed,
            "steps": args.steps,
            "threads": args.threads,
            "python": platform.python_version(),
            "torch": str(torch.__version__),
            "machine": platform.machine(),
            "device": "cpu",
            "entrainement_sha256": train_hash,
            "validation_sha256": validation_hash,
            "duree_secondes": round(perf_counter() - start, 2),
            "metriques": metrics,
            "octets_par_token_validation": tokenizer_metrics.bytes_per_token,
            "vocabulaire": len(tokenizer.vocabulary),
        }
        save_checkpoint(args.output, model, tokenizer, report)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Échec de l'entraînement : {error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Checkpoint : {args.output}")


if __name__ == "__main__":
    main()
