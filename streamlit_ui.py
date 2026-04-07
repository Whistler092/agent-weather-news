"""Streamlit-specific UI helpers (session state and chat rendering)."""

from __future__ import annotations

import streamlit as st


def render_chat_history() -> None:
    """Render all messages in st.session_state.messages as chat bubbles."""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def render_sidebar() -> None:
    st.sidebar.header("Configuration")
    st.sidebar.write("This app uses Azure OpenAI and two MCP servers")
    st.sidebar.code(
        "\n".join(
            [
                "LLM Model:",
                "- gpt-5-nano",
                "MCP servers:",
                "- Open-Meteo",
                "- Google News",
            ]
        )
    )