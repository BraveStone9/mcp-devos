import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVER_SCRIPT = PROJECT_ROOT / "server.py"
LOGS_DIR = PROJECT_ROOT / "logs"
MODEL_NAME = "gemini-3.5-flash-lite"
REQUEST_TIMEOUT_MS = 60_000

DEBUG_PROMPT = (
    "Something is wrong with the inventory app. Can you investigate and tell me "
    "what's broken and why?"
)


def setup_logging(log_file: Path) -> logging.Logger:
    formatter = logging.Formatter(
        fmt="%(asctime)s [client] %(message)s", datefmt="%H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.ERROR)

    return logging.getLogger("devos.client")


async def run_prompt(prompt: str) -> None:
    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / f"run_{datetime.now():%Y%m%d_%H%M%S}.log"
    logger = setup_logging(log_file)

    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.environ["GEMINI_API_KEY"]

    server_env = {**os.environ, "DEVOS_LOG_FILE": str(log_file)}
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_SCRIPT)],
        cwd=str(PROJECT_ROOT),
        env=server_env,
    )

    logger.info(f"Launching MCP server: {SERVER_SCRIPT.name}")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            logger.info("Connected to server. Initializing MCP session...")
            await session.initialize()

            tools = await session.list_tools()
            tool_names = ", ".join(t.name for t in tools.tools)
            logger.info(f"Session ready. Available tools: {tool_names}")

            logger.info(f"Sending prompt to {MODEL_NAME}: {prompt!r}")
            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
            )
            response = await client.aio.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={"tools": [session]},
            )
            logger.info("Received final response from the model.")

            print(response.text)

    print(f"\nFull step-by-step log saved to: {log_file.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    asyncio.run(run_prompt(DEBUG_PROMPT))
