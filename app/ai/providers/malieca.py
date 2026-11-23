"""Adaptateur AIModel pour les checkpoints expérimentaux de MALIECA-LLM."""

from pathlib import Path
from pickle import UnpicklingError

try:
    import torch
except ImportError as error:
    raise ImportError("Installez le supplément « llm » pour utiliser MALIECA-LLM.") from error

from app.ai.base import AIMessage, AIModel, AIResponse, AIToolDefinition
from app.ai.models.chat_format import ChatFormat
from app.ai.models.config import TransformerConfig
from app.ai.models.transformer import Transformer
from app.ai.tokenizers.bpe import BytePairTokenizer

CHECKPOINT_FORMAT = "malieca-llm-v1"


class MaliecaModel(AIModel):
    def __init__(self, transformer: Transformer, chat_format: ChatFormat) -> None:
        if transformer.config.vocab_size != chat_format.size:
            raise ValueError("Le vocabulaire du checkpoint ne correspond pas au modèle.")
        self.transformer = transformer.eval()
        self.chat_format = chat_format

    @classmethod
    def load(cls, path: Path) -> "MaliecaModel":
        try:
            checkpoint = torch.load(path, map_location="cpu", weights_only=True)
            if checkpoint["format"] != CHECKPOINT_FORMAT:
                raise ValueError("Format de checkpoint inconnu.")
            config = TransformerConfig(**checkpoint["config"])
            tokenizer = BytePairTokenizer(
                [(bytes.fromhex(left), bytes.fromhex(right)) for left, right in checkpoint["merges"]]
            )
            transformer = Transformer(config)
            transformer.load_state_dict(checkpoint["weights"])
        except (EOFError, KeyError, TypeError, UnpicklingError) as error:
            raise ValueError("Checkpoint MALIECA-LLM invalide.") from error
        return cls(transformer, ChatFormat(tokenizer))

    @torch.inference_mode()
    def generate(
        self,
        messages: list[AIMessage],
        tools: list[AIToolDefinition] | None = None,
    ) -> AIResponse:
        window = self.transformer.config.max_sequence_length
        budget = min(window // 2, 96)
        if budget == 0:
            raise RuntimeError("Fenêtre de contexte trop petite pour générer une réponse.")
        prefix = self.chat_format.prompt(messages)[-(window - budget):]
        generated: list[int] = []
        device = next(self.transformer.parameters()).device

        for _ in range(budget):
            inputs = torch.tensor([prefix + generated], dtype=torch.long, device=device)
            scores = self.transformer(inputs)[0, -1]
            byte_vocab = scores[:len(self.chat_format.tokenizer.vocabulary)]
            # Les seules sorties possibles sont des tokens de texte et la fin du message.
            if scores[self.chat_format.end] > byte_vocab.max():
                break
            generated.append(int(byte_vocab.argmax()))

        while generated:
            try:
                content = self.chat_format.tokenizer.decode(generated).strip()
                if content:
                    return AIResponse(content=content, metadata={"model": CHECKPOINT_FORMAT})
                break
            except UnicodeDecodeError as error:
                if error.reason == "unexpected end of data":
                    generated.pop()
                else:
                    break
        raise RuntimeError("Le modèle expérimental n'a pas produit de réponse UTF-8 exploitable.")
