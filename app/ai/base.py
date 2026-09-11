"""Abstractions for language models used by M.A.L.I.E.C.A."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AIMessage:
    """A message exchanged with an AI model."""

    role: str
    content: str


@dataclass(frozen=True)
class AIResponse:
    """Normalized response returned by an AI model."""

    content: str
    metadata: dict[str, object] = field(default_factory=dict)


class AIModel(ABC):
    """Contract implemented by every LLM provider."""

    @abstractmethod
    def generate(self, messages: list[AIMessage]) -> AIResponse:
        """Generate a response from a conversation."""
        raise NotImplementedError
