import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

DEVOS_ROOT = Path(os.getenv("DEVOS_ROOT", BASE_DIR / "demo")).resolve()

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".py",
    ".txt",
    ".log",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".cfg",
    ".ini",
    ".csv",
}
