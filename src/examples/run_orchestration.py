import asyncio
import os
from google.genai import types

from pathlib import Path

from dotenv import load_dotenv
from google import genai


from agent_lab.agents.developer import DeveloperAgent
from agent_lab.agents.reviewer import ReviewerAgent
from agent_lab.models.gemini_provider import GeminiModelProvider
from agent_lab.orchestration.orchestrator import AgentOrchestrator


async def main():
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")

    for name in ("GEMINI_API_KEY", "GEMINI_MODEL"):
        if not os.environ.get(name):
            raise ValueError(f"Configurazione mancante: {name}")

    async with genai.Client(
            api_key=os.environ["GEMINI_API_KEY"],
    ).aio as client:
        developer_provider = GeminiModelProvider(
            client=client,
            model=os.environ["GEMINI_MODEL"],
        )

        reviewer_provider = GeminiModelProvider(
            client=client,
            model=os.environ["GEMINI_MODEL"],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema={
                    "type": "object",
                    "properties": {
                        "approved": {"type": "boolean"},
                        "feedback": {"type": "string"},
                    },
                    "required": ["approved", "feedback"],
                    "additionalProperties": False,
                },
            ),
        )

        orchestrator = AgentOrchestrator(
            developer=DeveloperAgent(developer_provider),
            reviewer=ReviewerAgent(reviewer_provider),
            max_attempts=3,
        )

        result = await orchestrator.run(
            "Proponi una funzione Python che divide due numeri "
            "e gestisce la divisione per zero."
        )

        print("Proposta:")
        print(result.proposal)
        print("\nApprovata:", result.review.approved)
        print("Feedback:", result.review.feedback)


if __name__ == "__main__":
    asyncio.run(main())