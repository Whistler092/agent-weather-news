# Agent Weather & News

A small **Streamlit** chat app that answers questions about **weather**, **news**, and a demo **music** tool. The assistant is powered by **Azure OpenAI** and **LangChain**’s agent runtime (`create_agent` / LangGraph). Live data comes from **two MCP servers** (Model Context Protocol) wired through **`langchain-mcp-adapters`**: no separate news or weather API keys are required for the integrations chosen here.

## What it does

- **Weather & related**: current conditions, forecasts, air quality, and time/timezone helpers via the **[open-meteo-mcp](https://pypi.org/project/open-meteo-mcp/)** server (Open-Meteo data, no API key).
- **News**: headlines and search-style feeds via **[mcp-server-google-news](https://pypi.org/project/mcp-server-google-news/)** (Google News RSS; no provider API key).
- **Demo tool**: `music_prediction` is a local LangChain tool used for simple “future music” style prompts.

The UI shows **progress** (tool calls, completions) and **streams** the model reply where supported. A short **sidebar** summarizes the setup.

## Architecture (high level)

```text
User (Streamlit) → LangGraph agent (Azure Chat) → Tools
                      ├── MCP: Open-Meteo (stdio)
                      ├── MCP: Google News (stdio, console script on PATH)
                      └── music_prediction (@tool)
```

## Requirements

- **Python** 3.10+ (3.13 works with current dependencies in many setups).
- **Azure OpenAI** resource with a chat deployment.
- Network access for Open-Meteo, Google News RSS, and Azure.

## Setup

1. Clone or copy this repository.

2. Create a virtual environment (recommended):

   **Windows (PowerShell)**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If activation is blocked by execution policy, run this once and try again:

   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```

   **macOS/Linux**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (see below). You can use a `.env` file in the project root; the app loads it via `python-dotenv`.

5. (Optional) Deactivate the environment when you are done:

   ```bash
   deactivate
   ```

## Environment variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_ENDPOINT` | Azure OpenAI endpoint URL (e.g. `https://<resource>.openai.azure.com/`) |
| `MODEL` | **Deployment name** of your chat model (must match the name in Azure AI Studio / portal) |

## Run the app

```bash
streamlit run streamlit_agent.py
```

Open the URL shown in the terminal (by default `http://localhost:8501`). Watch the terminal for **INFO** logs while the agent runs.

## Project layout (main files)

I am not very proficient with Python, so I asked AI code agent to help me cleaning the code into specific folders.

| Path | Purpose |
|------|---------|
| `streamlit_agent.py` | App entry: `load_agent`, chat UI, tool definitions |
| `mcp_stack_provider.py` | `MultiServerMCPClient` config for Open-Meteo + Google News |
| `agent_streaming.py` | Streaming run loop and status updates |
| `agent_messages.py` | Helpers to read assistant text from graph state |
| `conversation.py` | History formatting and user message construction |
| `app_config.py` | Constants, logging, env validation |
| `streamlit_ui.py` | Chat history and sidebar rendering |

## Example prompts

- “What’s the weather like in Paris today?”
- “Top technology headlines in the US”
- (Demo) “Best rock band in 2050?” — exercises the `music_prediction` tool

## Notes

- **GNews.io / NewsAPI / similar** were not used as the default stack because they typically require API keys; this project prioritizes **keyless** RSS/Open-Meteo paths for local demos.
- First load after install may take a few seconds while MCP subprocesses start and tools are listed.
- If the Google News MCP fails to start, ensure `mcp-server-google-news` is on your **PATH** after `pip install` (on Windows, the `Scripts` folder of your environment).
