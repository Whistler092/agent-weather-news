from __future__ import annotations

import asyncio
import sys
from typing import List

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


class OpenMeteoMCPProvider:
    """Loads LangChain tools from the open-meteo-mcp MCP server over stdio."""

    def __init__(self, *, tool_name_prefix: bool = True) -> None:
        self._tool_name_prefix = tool_name_prefix

    def _client(self) -> MultiServerMCPClient:
        return MultiServerMCPClient(
            {
                "open_meteo": {
                    "transport": "stdio",
                    "command": sys.executable,
                    "args": ["-m", "open_meteo_mcp"],
                }
            },
            tool_name_prefix=self._tool_name_prefix,
        )

    async def _async_get_tools(self) -> List[BaseTool]:
        return await self._client().get_tools()

    def get_tools(self) -> List[BaseTool]:
        """Synchronous entrypoint for Streamlit and other sync callers."""
        return asyncio.run(self._async_get_tools())
