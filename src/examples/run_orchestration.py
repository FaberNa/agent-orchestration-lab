import asyncio
import os
import ast

from google.genai import types

from pathlib import Path

from dotenv import load_dotenv
from google import genai


from agent_lab.agents.developer import DeveloperAgent
from agent_lab.agents.reviewer import ReviewerAgent
from agent_lab.models.gemini_provider import GeminiModelProvider
from agent_lab.orchestration.orchestrator import AgentOrchestrator
from agent_lab.models.gemini_tool_provider import GeminiToolProvider
from agent_lab.tools.read_file import ReadFileTool

async def main():
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")

    for name in ("GEMINI_API_KEY", "GEMINI_MODEL"):
        if not os.environ.get(name):
            raise ValueError(f"Configurazione mancante: {name}")

    async with genai.Client(
            api_key=os.environ["GEMINI_API_KEY"],
    ).aio as client:
        developer_provider = GeminiToolProvider(
            client=client,
            model=os.environ["GEMINI_MODEL"],
            reader=ReadFileTool(
                Path(__file__).resolve().parents[2] / "workspace"
            ),
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

        #result = await orchestrator.run(
        #    "Proponi una funzione Python che divide due numeri "
        #    "e gestisce la divisione per zero."
        #)
        #result = await orchestrator.run(
        #    "Leggi calculator.py usando read_file. "
        #    "Spiega cosa fa e proponi come migliorare "
        #    "la gestione della divisione per zero. "
        #    "Non modificare il file."
        #)

        result = await orchestrator.run(
            "Leggi calculator.py usando read_file e proponi una versione corretta.\n"
            "Requisiti:\n"
            "- divide(a, b) deve restituire il quoziente.\n"
            "- Se b è zero, deve sollevare ValueError.\n\n"
            "Risultato dei test sull'implementazione attuale:\n"
            "3 passed, 1 failed.\n"
            "Il test test_divide_rejects_zero_divisor si aspetta ValueError,\n"
            #"ma la funzione solleva ZeroDivisionError.\n\n"
            #"Restituisci il codice completo proposto per calculator.py.\n"
            #"Non modificare i file."
            "Restituisci esclusivamente il codice Python completo per calculator.py.\n"
            "Non usare blocchi Markdown, delimitatori ``` o spiegazioni.\n"
            "Non modificare i file."
        )
        if not result.review.approved:
            print("Proposta non approvata: il file non viene aggiornato.")
            print(result.review.feedback)
            return

        # Verifica la sintassi senza eseguire il codice.
        ast.parse(result.proposal)

        target = Path(__file__).resolve().parents[2] / "workspace" / "calculator.py"
        target.write_text(result.proposal + "\n", encoding="utf-8")

        print(f"Proposta salvata in: {target}")

        print("Proposta:")
        print(result.proposal)
        print("\nApprovata:", result.review.approved)
        print("Feedback:", result.review.feedback)


if __name__ == "__main__":
    asyncio.run(main())