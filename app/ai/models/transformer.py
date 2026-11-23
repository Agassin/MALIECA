"""Décodeur autorégressif expérimental de MALIECA-LLM."""

import torch
from torch import Tensor, nn

from app.ai.models.config import TransformerConfig


class Transformer(nn.Module):
    def __init__(self, config: TransformerConfig) -> None:
        super().__init__()
        self.config = config
        self.tokens = nn.Embedding(config.vocab_size, config.d_model)
        self.positions = nn.Embedding(config.max_sequence_length, config.d_model)
        self.blocks = nn.ModuleList(
            nn.TransformerEncoderLayer(
                d_model=config.d_model,
                nhead=config.num_heads,
                dim_feedforward=config.feed_forward_dim,
                dropout=config.dropout,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            for _ in range(config.num_layers)
        )
        self.norm = nn.LayerNorm(config.d_model)
        self.output = nn.Linear(config.d_model, config.vocab_size, bias=False)

    def forward(self, token_ids: Tensor) -> Tensor:
        if token_ids.ndim != 2 or not 1 <= token_ids.shape[1] <= self.config.max_sequence_length:
            raise ValueError("Les tokens doivent former un lot de séquences de longueur valide.")
        length = token_ids.shape[1]
        positions = torch.arange(length, device=token_ids.device)
        hidden = self.tokens(token_ids) + self.positions(positions)
        causal_mask = torch.ones(length, length, device=token_ids.device, dtype=torch.bool).triu(1)
        for block in self.blocks:
            hidden = block(hidden, src_mask=causal_mask, is_causal=True)
        return self.output(self.norm(hidden))
