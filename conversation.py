"""Formatting chat history and building LangChain messages for the agent."""

from __future__ import annotations

from typing import List

from langchain_core.messages import HumanMessage


def format_history(messages: List[dict]) -> str:
    """
    Turn session message dicts into a compact text block for the model.

    Only the last six turns are included to limit prompt size.
    """
    recent = messages[-6:]
    lines = [f"{item.get('role', 'user')}: {item.get('content', '')}" for item in recent]
    return "\n".join(lines)


def build_user_message(history: str, question: str) -> HumanMessage:
    """Wrap history and the latest user question in a single HumanMessage for the agent graph."""
    text = f"History:\n{history}\n\nQuestion:\n{question}\n\nAnswer:"
    return HumanMessage(content=text)
