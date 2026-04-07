"""Run the LangGraph agent with streamed tokens and status updates (MCP tools require async)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, List, Optional, cast

import streamlit as st
from langchain_core.messages import BaseMessage

from agent_messages import (
    describe_message_for_status,
    last_assistant_reply,
)
from conversation import build_user_message

logger = logging.getLogger(__name__)


def normalize_astream_event(raw: Any) -> Optional[dict[str, Any]]:
    """
    Coerce LangGraph astream chunks to a dict with 'type' and 'data' keys.

    Supports v2 dict events and v1 (mode, payload) tuples.
    """
    if isinstance(raw, dict) and raw.get("type") is not None:
        return raw
    if isinstance(raw, tuple) and len(raw) == 2:
        return {"type": raw[0], "data": raw[1]}
    return None


def message_chunk_to_text_delta(msg_chunk: Any) -> str:
    """Extract incremental text from a streamed message chunk (LLM token or block)."""
    chunk = getattr(msg_chunk, "content", None)
    if isinstance(chunk, str):
        return chunk
    if isinstance(chunk, list):
        return "".join(
            str(block.get("text", ""))
            for block in chunk
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def unwrap_messages_event_payload(data: Any) -> Any:
    """Unwrap (message, metadata) tuples produced by stream_mode='messages'."""
    if isinstance(data, tuple) and len(data) >= 1:
        return data[0]
    return data


def make_status_emitter(status_container: Any) -> Callable[[str], None]:
    """
    Create a callback that logs a line and appends it to the Streamlit status widget.

    Falls back to st.caption if status.write is unavailable.
    """

    def emit(line: str) -> None:
        logger.info("%s", line)
        try:
            status_container.write(line)
        except Exception:
            st.caption(line)

    return emit


async def stream_agent_to_completion(
    agent: Any,
    inputs: dict[str, Any],
    *,
    emit_status: Callable[[str], None],
    stream_placeholder: Any,
) -> str:
    """
    Drive agent.astream with values + messages modes: update status on graph values, stream tokens to the placeholder.

    Returns the final assistant string taken from graph state (authoritative).
    """
    last_state: dict[str, Any] | None = None
    previous_message_count = 0
    streamed_chars = ""

    async for raw in agent.astream(
        inputs,
        stream_mode=["values", "messages"],
        version="v2",
    ):
        event = normalize_astream_event(raw)
        if event is None:
            continue

        mode = event.get("type")
        if mode == "values":
            data = event.get("data")
            if not isinstance(data, dict):
                continue
            last_state = data
            messages = cast(List[BaseMessage], data.get("messages") or [])
            if len(messages) > previous_message_count:
                for message in messages[previous_message_count:]:
                    line = describe_message_for_status(message)
                    if line:
                        emit_status(line)
                previous_message_count = len(messages)

        elif mode == "messages":
            msg_chunk = unwrap_messages_event_payload(event.get("data"))
            delta = message_chunk_to_text_delta(msg_chunk)
            if delta:
                streamed_chars += delta
                stream_placeholder.markdown(streamed_chars + "▍")

    final_text = last_assistant_reply(last_state) if last_state else ""
    stream_placeholder.markdown(final_text or streamed_chars)
    return final_text


def run_agent_sync(
    agent: Any,
    history: str,
    question: str,
    *,
    status_container: Any,
    stream_placeholder: Any,
) -> str:
    """Synchronous entry: build inputs, wire status streaming, asyncio.run the async streamer."""
    inputs = {"messages": [build_user_message(history, question)]}
    emit_status = make_status_emitter(status_container)

    async def _run() -> str:
        return await stream_agent_to_completion(
            agent,
            inputs,
            emit_status=emit_status,
            stream_placeholder=stream_placeholder,
        )

    return asyncio.run(_run())
