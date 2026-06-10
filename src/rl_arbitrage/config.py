import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
DATA_DIR = PROJECT_ROOT / "data" / "historical" / "BTCUSDT"

SYMBOL = "BTCUSDT"
DEFAULT_TARGET_DATES = [
    "2026-05-01",
    "2026-05-02",
    "2026-05-03",
    "2026-05-04",
    "2026-05-05",
    "2026-05-06",
    "2026-05-07",
]


def get_api_key() -> str:
    key = os.environ.get("CRYPTOHFTDATA_API_KEY")
    if not key:
        raise EnvironmentError(
            "CRYPTOHFTDATA_API_KEY is not set. "
            "Copy .env.example to .env and add your API key."
        )
    return key
