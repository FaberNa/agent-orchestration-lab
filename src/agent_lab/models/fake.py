from agent_lab.models.base import ModelProvider


class FakeModelProvider(ModelProvider):
    """Deterministic model provider used for testing."""

    def __init__(self, response: str = "Fake model response"):
        self.response = response
        self.last_prompt: str | None = None

    async def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.response