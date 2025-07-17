"""
Configuration management for TrainingReadiness project.
Loads environment variables and provides configuration values.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).resolve().parent
load_dotenv(project_root / ".env")


def get_hevy_api_key() -> str:
    """Load Hevy API key from environment variable HEVY_API_KEY."""
    api_key = os.getenv("HEVY_API_KEY")
    if not api_key:
        raise ValueError("HEVY_API_KEY not found in environment variables")
    return api_key


def get_timezone_offset_hours() -> int:
    """Load timezone offset from environment variable TIMEZONE_OFFSET_HOURS (integer hours, e.g. -7)."""
    offset = os.getenv("TIMEZONE_OFFSET_HOURS", "0")
    try:
        return int(offset)
    except ValueError:
        raise ValueError(
            f"Invalid TIMEZONE_OFFSET_HOURS value: {offset}. Must be an integer."
        )
