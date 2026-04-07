"""Extract human-readable text and progress hints from LangChain messages and agent state."""

from __future__ import annotations

from typing import Any, List, Optional, cast

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage


def tool_call_names(tool_calls: List[Any]) -> List[str]:
    """Return display names for tool calls whether they are dicts or objects."""
    out: List[str] = []
    for tc in tool_calls:
        if isinstance(tc, dict):
            out.append(str(tc.get("name", "?")))
        else:
            out.append(str(getattr(tc, "name", "?")))
    return out


def describe_message_for_status(message: BaseMessage) -> Optional[str]:
    """
    Build a short status line when new messages appear during streaming.

    Used to show tool calls and tool completions in the Streamlit status box.
    """
    if isinstance(message, ToolMessage):
        return f"Tool finished: `{message.name}`"
    if isinstance(message, AIMessage) and message.tool_calls:
        return f"Calling tools: {', '.join(tool_call_names(message.tool_calls))}"
    return None


def assistant_text_from_message(message: AIMessage) -> str:
    """Normalize AIMessage.content to a plain string (string, or list of content blocks)."""
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)
    return ""


def last_assistant_reply(state: dict[str, Any]) -> str:
    """Read the final assistant text from the graph state after a run completes."""
    msgs: List[BaseMessage] = cast(List[BaseMessage], state.get("messages") or [])
    if not msgs:
        return ""
    last = msgs[-1]
    if isinstance(last, AIMessage):
        return assistant_text_from_message(last)
    return str(getattr(last, "content", "") or "")
