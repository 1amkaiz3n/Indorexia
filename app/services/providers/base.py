"""Abstract base for all AI providers."""

from abc import ABC, abstractmethod


class AIProvider(ABC):
    name: str

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Call the provider and return raw response text.
        Raise AIProviderError on any failure (rate limit, timeout, bad response, etc)."""
        ...


class AIProviderError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)
