import asyncio
from google.genai import types
from google.genai.client import AsyncClient

from agent_lab.models.base import ModelProvider


class GeminiModelProvider(ModelProvider):
    """Model provider backed by the Gemini API."""

    def __init__(
            self,
            client: AsyncClient,
            model: str,
            config: types.GenerateContentConfig | None = None,
    ):
        self.client = client
        self.model = model
        self.config = config

    async def generate(self, prompt: str) -> str:
        async with asyncio.timeout(60):
            response = await self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self.config,
            )

        if not response.text:
            raise RuntimeError("Gemini did not return a text response")

        return response.text