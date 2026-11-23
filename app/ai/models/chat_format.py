"""Format de dialogue commun à l'entraînement et à l'inférence."""

from app.ai.base import AIMessage
from app.ai.tokenizers.bpe import BytePairTokenizer


class ChatFormat:
    ROLES = ("system", "user", "assistant", "tool")

    def __init__(self, tokenizer: BytePairTokenizer) -> None:
        self.tokenizer = tokenizer
        base = len(tokenizer.vocabulary)
        self.roles = {role: base + index for index, role in enumerate(self.ROLES)}
        self.end = base + len(self.ROLES)
        self.size = self.end + 1

    def prompt(self, messages: list[AIMessage]) -> list[int]:
        tokens: list[int] = []
        for message in messages:
            tokens += [self.roles[message.role], *self.tokenizer.encode(message.content), self.end]
        return [*tokens, self.roles["assistant"]]

    def completion(self, content: str) -> list[int]:
        return [*self.tokenizer.encode(content), self.end]
