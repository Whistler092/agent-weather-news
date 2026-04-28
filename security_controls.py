"""Security helpers for prompt-injection resistance and safe error handling."""

from __future__ import annotations

import re
from typing import List

# Simple, explicit patterns used for educational red-teaming demos.
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"\bignore (all )?(previous|prior) (instructions|rules)\b", re.IGNORECASE),
    re.compile(r"\breveal (the )?(system prompt|developer message|hidden prompt)\b", re.IGNORECASE),
    re.compile(r"\bact as (system|developer)\b", re.IGNORECASE),
    re.compile(r"\bdo not use tools\b", re.IGNORECASE),
    re.compile(r"\boverride\b.*\binstructions\b", re.IGNORECASE),
]

MAX_USER_CHARS = 800


def find_prompt_injection_signals(text: str) -> List[str]:
    """Return matching rule names for suspicious prompt-injection phrases."""
    matches: List[str] = []
    for idx, pattern in enumerate(PROMPT_INJECTION_PATTERNS, start=1):
        if pattern.search(text or ""):
            matches.append(f"rule_{idx}")
    return matches


def validate_user_prompt(text: str) -> tuple[bool, str]:
    """Validate user input length and common prompt-injection signatures."""
    if len(text) > MAX_USER_CHARS:
        return False, f"Your message is too long ({len(text)} chars). Limit is {MAX_USER_CHARS}."

    hits = find_prompt_injection_signals(text)
    if hits:
        return (
            False,
            "Your request appears to contain instruction-override patterns. "
            "Please rephrase as a normal weather/news question.",
        )
    return True, ""


def safe_user_error() -> str:
    """Generic UI-safe error for end users."""
    return (
        "The assistant could not complete your request right now. "
        "Please try again in a moment."
    )
