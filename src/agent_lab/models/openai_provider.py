from openai import AsyncOpenAI

from agent_lab.models.base import ModelProvider


class OpenAIModelProvider(ModelProvider):
    """Model provider backed by the OpenAI Responses API."""

    def __init__(self, client: AsyncOpenAI, model: str):
        self.client = client
        self.model = model

    async def generate(self, prompt: str) -> str:
        response = await self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        if response.status != "completed" or not response.output_text:
            raise RuntimeError("The model did not return a complete text response")

        return response.output_text