import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


async def main():
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")

    model = os.environ["GEMINI_MODEL"]
    print(f"Modello: {model}", flush=True)

    async with genai.Client(
            api_key=os.environ["GEMINI_API_KEY"],
    ).aio as client:
        try:
            async with asyncio.timeout(20):
                response = await client.models.generate_content(
                    model=model,
                    contents="Rispondi soltanto con: OK",
                )
            print(response.text)
        except TimeoutError:
            print("Nessuna risposta entro 60 secondi.")


if __name__ == "__main__":
    asyncio.run(main())