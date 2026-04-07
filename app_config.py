"""Application constants, environment checks, and logging setup for the Streamlit agent."""

from __future__ import annotations

import logging
import os
from typing import Tuple

# Azure OpenAI API version used for chat completions.
API_VERSION = "2024-08-01-preview"

# Injected into create_agent(); tells the model how to use MCP tools and music_prediction.
SYSTEM_PROMPT = (
    "You are a helpful assistant for news and weather. "
    "For current weather, forecasts, air quality, or time/timezone questions, use the Open-Meteo MCP tools "
    "(names like open_meteo_get_current_weather). Pass the city in English as the tool expects (e.g. city parameter). "
    "For latest news, headlines, or topic feeds, use the Google News MCP tools "
    "(e.g. google_news_google_news_search, google_news_google_news_topics). "
    "Those tools default to Japanese; for English users pass hl=\"en\" and set gl to a region code when helpful "
    "(e.g. US, GB). "
    "For hypothetical or future music questions, use the music_prediction tool. "
    "Always use the appropriate tool for weather, news, air quality, or music rather than guessing."
)


def configure_logging() -> None:
    """Configure root logging once so INFO lines appear in the terminal (e.g. when running `streamlit run`)."""
    if logging.root.handlers:
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def validate_env() -> Tuple[bool, str]:
    """
    Verify required environment variables for Azure OpenAI are present.

    Returns:
        (True, "") if all required variables are set; otherwise (False, error message).
    """
    required_vars = ["OPENAI_API_KEY", "MODEL", "AZURE_ENDPOINT"]
    missing = [name for name in required_vars if not os.getenv(name)]
    if missing:
        return False, f"Missing environment variables: {', '.join(missing)}"
    return True, ""
