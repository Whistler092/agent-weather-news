from __future__ import annotations

import asyncio
import shutil
import sys
from typing import List

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

# GNews.io / NewsAPI / TheNews were not used here because they require API keys.
# mcp-server-google-news reads public Google News RSS (no provider key).
# The package's `python -m mcp_server_google_news` entrypoint is broken upstream;
# use the `mcp-server-google-news` console script from PATH instead.


def _google_news_stdio_config() -> dict[str, str | list[str]]:
    exe = shutil.which("mcp-server-google-news")
    if not exe:
        raise RuntimeError(
            "mcp-server-google-news is not on PATH. Install it with: pip install mcp-server-google-news"
        )
    return {
        "transport": "stdio",
        "command": exe,
        "args": [],
    }


class MCPStackProvider:
    """Loads LangChain tools from Open-Meteo and Google News RSS MCP servers (stdio, one client)."""

    def __init__(self, *, tool_name_prefix: bool = True) -> None:
        self._tool_name_prefix = tool_name_prefix

    def _client(self) -> MultiServerMCPClient:
        return MultiServerMCPClient(
            {
                "open_meteo": {
                    "transport": "stdio",
                    "command": sys.executable,
                    "args": ["-m", "open_meteo_mcp"],
                },
                "google_news": _google_news_stdio_config(),
            },
            tool_name_prefix=self._tool_name_prefix,
        )

    async def _async_get_tools(self) -> List[BaseTool]:
        return await self._client().get_tools()

    def get_tools(self) -> List[BaseTool]:
        """Synchronous entrypoint for Streamlit and other sync callers."""
        return asyncio.run(self._async_get_tools())
