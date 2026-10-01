from abc import ABC, abstractmethod


class ModelProvider(ABC):
    """Abstraction for language model providers."""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a response for the given prompt."""
        pass