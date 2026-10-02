import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVER_SCRIPT = PROJECT_ROOT / "server.py"
MODEL_NAME = "gemini-3.5-flash-lite"

DEBUG_PROMPT = (
    "Something is wrong with the inventory app. Can you investigate and tell me "
    "what's broken and why?"
)


async def run_prompt(prompt: str) -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.environ["GEMINI_API_KEY"]

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_SCRIPT)],
        cwd=str(PROJECT_ROOT),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            client = genai.Client(api_key=api_key)
            response = await client.aio.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={"tools": [session]},
            )

            print(response.text)


if __name__ == "__main__":
    asyncio.run(run_prompt(DEBUG_PROMPT))
