from __future__ import annotations

import asyncio
import os
from typing import List, Tuple


import streamlit as st
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    # Allow app startup in environments where python-dotenv is not installed.
    def load_dotenv(*args, **kwargs):
        return False

from langchain.agents import create_agent
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from mcp_stack_provider import MCPStackProvider

API_VERSION = "2024-08-01-preview"


def format_history(messages: List[dict]) -> str:
    # Use the last 6 turns to keep prompt size controlled.
    recent = messages[-6:]
    lines: List[str] = []
    for item in recent:
        role = item.get("role", "user")
        content = item.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def validate_env() -> Tuple[bool, str]:
    required_vars = ["OPENAI_API_KEY", "MODEL", "AZURE_ENDPOINT"]
    missing = [name for name in required_vars if not os.getenv(name)]
    if missing:
        return False, f"Missing environment variables: {', '.join(missing)}"
    return True, ""

# Create an application, that could answer questions about current weather and latest news with Python + Streamlit, 
#    using Agent orchestrators 
#        and MCP servers for Open‑Meteo and TheNews API / GNews.io / NewsAPI without API Key (choose one news web-site mcp).
#At least one evaluation metric is defined, evaluated, and demonstrated (quantitative or qualitative measure used to assess the performance, quality, and safety of generative model outputs). 
#You need to have at least small evaluation data set and for at least one criterion.

# Weather + keyless news: Open-Meteo MCP and Google News RSS MCP (see mcp_stack_provider.py).

@tool
def music_prediction(question: str) -> str:
    """Predicts music trends and answers questions about future music."""
    print(f"Received question: {question} for music prediction tool.")
    return "The Beatles will be resurrected by AI and will be the best rock band in 2050."


@st.cache_resource(show_spinner=False)
def load_agent() -> create_agent:
    load_dotenv()

    ok, message = validate_env()
    if not ok:
        raise RuntimeError(message)
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("MODEL")
    azure_endpoint = os.getenv("AZURE_ENDPOINT")

    print(f"Loading AzureChatOpenAI with endpoint: {azure_endpoint}, model: {model}")

    if not azure_endpoint or not openai_api_key:
        raise ValueError("Azure OpenAI endpoint and key must be set in environment variables.")
    llm = AzureChatOpenAI(
        api_key=openai_api_key,
        api_version="2024-08-01-preview",
        azure_endpoint=azure_endpoint,
        azure_deployment=model,
        temperature=1
    )

    mcp_tools = MCPStackProvider().get_tools()
    tools = list(mcp_tools) + [music_prediction]
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a helpful assistant for news and weather. "
            "For current weather, forecasts, air quality, or time/timezone questions, use the Open-Meteo MCP tools "
            "(names like open_meteo_get_current_weather). Pass the city in English as the tool expects (e.g. city parameter). "
            "For latest news, headlines, or topic feeds, use the Google News MCP tools "
            "(e.g. google_news_google_news_search, google_news_google_news_topics). "
            "Those tools default to Japanese; for English users pass hl=\"en\" and set gl to a region code when helpful "
            "(e.g. US, GB). "
            "For hypothetical or future music questions, use the music_prediction tool. "
            "Always use the appropriate tool for weather, news, air quality, or music rather than guessing."
        ),
    )
    
    return agent

def ask_agent(agent: create_agent, question: str, history: str) -> Tuple[str, List[Tuple[Document, float]]]:
    print("asking agent")
    print(history)
    print(question)
    message = f"History:\n{history}\n\nQuestion:\n{question}\n\nAnswer:"

    async def _run() -> dict:
        # MCP-backed tools from langchain-mcp-adapters are async-only; use ainvoke, not invoke.
        return await agent.ainvoke({"messages": [HumanMessage(content=message)]})

    response = asyncio.run(_run())
    return response["messages"][-1].content, []
                                        # f"History:\n{history}\n\nQuestion:\n{question}\n\nAnswer:")])

def main() -> None:
    st.title("My daily news and weather agent")
    st.caption("This agent retrieves the latest news and weather information for a specified location.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello. Ask me anything about the news and weather in any location. For example, you can ask 'What's the weather like in New York today?' or 'What are the latest news headlines in London?'",
            }
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type your question...")
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching information and generating answer..."):
            try:
                agent = load_agent()
                history_text = format_history(st.session_state.messages)
                answer, retrieved = ask_agent(agent, user_input, history_text)
            except Exception as exc:
                st.error(f"Error: {exc}")
                return

        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()