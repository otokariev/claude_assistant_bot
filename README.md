# Claude Assistant Bot

A feature-rich Telegram bot powered by the Anthropic Claude API. Built as a reference project covering all major topics from the **"Building with the Claude API"** course — including tool use, MCP, RAG, agentic workflows, structured outputs, and more.

---

## What the bot can do

| Command | Description |
|---|---|
| `/help` | Show all available commands |
| `/clear` | Clear conversation history |
| `/stream` | Stream response word by word |
| `/memory` | Show saved facts about you |
| `/forget` | Clear long-term memory |
| `/note` | Manage notes via Tool Use |
| `/mcp` | Manage notes via MCP (STDIO) |
| `/mcp_http` | Manage notes via MCP (HTTP) |
| `/roots` | Show directories accessible to MCP server |
| `/upload` | Upload text to knowledge base |
| `/ask_with_rag` | Ask a question about uploaded documents |
| `/summarize_note` | Summarize a note using MCP Sampling |
| `/process_notes` | Process all notes with progress notifications |
| `/chain` | Sequential chain: translate → summarize → bullet points |
| `/parallel` | Parallel analysis of text from three angles |
| `/route` | Auto-detect request type and respond accordingly |
| `/sentiment` | Analyze sentiment of text |
| `/tasks` | Extract tasks and deadlines from text |
| `/test` | Run prompt quality tests (LLM-as-a-judge) |
| `/benchmark` | Benchmark Haiku vs Sonnet response speed |

---

## Tech stack

- **Python 3.12**
- **aiogram 3** — Telegram bot framework
- **anthropic** — Claude API (Haiku + Sonnet)
- **mcp** — Model Context Protocol
- **chromadb** — vector store for RAG
- **sentence-transformers** — text embeddings (`all-MiniLM-L6-v2`)
- **aiohttp** — webhook server
- **uvicorn** — ASGI server for MCP HTTP
- **python-dotenv** — environment variables
- **uv** — package manager
- **Render** — hosting
- **GitHub** — repository

---

## Project architecture

```
claude_assistant_bot/
├── main.py                        # entry point (webhook server)
│
├── bot/
│   ├── config.py                  # settings, models, constants
│   ├── handlers.py                # all Telegram command handlers
│   └── keyboard.py                # reply keyboard with all commands
│
├── claude/
│   ├── client.py                  # base Claude client + tool use + memory
│   ├── conversation.py            # per-user conversation history manager
│   ├── streaming.py               # streaming responses
│   ├── structured.py              # structured JSON outputs
│   └── tools.py                   # tool definitions for Claude API
│
├── tools/
│   └── notes_tool.py              # notes CRUD (stored in notes.json)
│
├── mcp_module/
│   ├── mcp_server.py              # MCP server (STDIO) with tools, resources, prompts
│   ├── mcp_client.py              # MCP client (STDIO) with sampling + roots support
│   ├── mcp_server_http.py         # MCP server (StreamableHTTP) for production
│   └── mcp_client_http.py         # MCP client (HTTP)
│
├── rag/
│   ├── embeddings.py              # text → vector via sentence-transformers
│   ├── vector_store.py            # ChromaDB storage and search
│   └── retrieval.py               # RAG pipeline
│
├── workflows/
│   ├── chains.py                  # sequential chain workflow
│   ├── parallel.py                # parallel analysis workflow
│   └── routing.py                 # request routing workflow
│
├── memory/
│   ├── memory_store.py            # long-term facts storage (memory.json)
│   └── memory_manager.py         # extract facts + inject into system prompt
│
├── evals/
│   ├── test_prompts.py            # LLM-as-a-judge prompt quality tests
│   └── benchmarks.py             # model speed benchmarks
│
├── .env                           # secret keys (not in Git)
├── .gitignore
├── pyproject.toml
└── uv.lock
```

---

## Getting started locally

**1. Clone the repository:**
```bash
git clone https://github.com/your-username/claude_assistant_bot.git
cd claude_assistant_bot
```

**2. Install dependencies:**
```bash
uv sync --python 3.12
```

**3. Create `.env` file:**
```
ANTHROPIC_API_KEY=your_anthropic_key
TELEGRAM_BOT_TOKEN=your_telegram_token
BOT_PASSWORD=your_password
```

**4. Run the bot (polling mode for local development):**

Uncomment the polling section at the bottom of `main.py` and comment out the webhook section, then:
```bash
uv run main.py
```

---

## Deploying to Render

### Deploy the Telegram bot

**1.** Push your code to GitHub.

**2.** Go to [render.com](https://render.com) → **New** → **Web Service** → connect your repository.

**3.** Configure the service:
- **Build Command:** `uv sync --frozen && uv cache prune --ci`
- **Start Command:** `uv run main.py`
- **Instance Type:** Free

**4.** Add environment variables:
```
ANTHROPIC_API_KEY=...
TELEGRAM_BOT_TOKEN=...
WEBHOOK_HOST=https://your-service.onrender.com
BOT_PASSWORD=...
```

**5.** Deploy and wait for the service to go live.

**6.** Set up [UptimeRobot](https://uptimerobot.com) to ping `https://your-service.onrender.com/health` every 5 minutes — prevents the free tier from sleeping.

**7.** Verify webhook is set:
```
https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```
If `url` is empty, set it manually:
```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://your-service.onrender.com/webhook
```

---

### Deploy the MCP HTTP server (optional, separate service)

The bot includes an HTTP transport MCP server (`mcp_module/mcp_server_http.py`) that can be deployed as a separate service for production use. This allows any MCP-compatible client to connect to it remotely.

**1.** Create a second **Web Service** on Render from the same repository.

**2.** Configure the service:
- **Build Command:** `uv sync --frozen && uv cache prune --ci`
- **Start Command:** `uv run python mcp_module/mcp_server_http.py`
- **Instance Type:** Free

**3.** Add environment variables:
```
ANTHROPIC_API_KEY=...
```

**4.** After deployment, get the service URL (e.g. `https://mcp-server.onrender.com`).

**5.** Update `MCP_SERVER_URL` in `mcp_module/mcp_client_http.py`:
```python
MCP_SERVER_URL = "https://mcp-server.onrender.com/mcp"
```

**6.** Push the change and redeploy the main bot service.

**Why two services?**
- STDIO transport (`/mcp`) — for local development only, server runs as a subprocess
- HTTP transport (`/mcp_http`) — for production, server runs independently and multiple clients can connect

---

## Key concepts demonstrated

- **Multi-turn conversation** with per-user history management
- **Streaming** responses via Anthropic SDK
- **Tool use** with agentic loop (`while True` until `end_turn`)
- **MCP (Model Context Protocol)** — STDIO and StreamableHTTP transports, tools, resources, prompts, sampling, notifications, roots
- **RAG** with ChromaDB and sentence-transformers
- **Agentic workflows** — sequential chains, parallel execution, request routing
- **Structured outputs** — JSON schema responses from Claude
- **LLM-as-a-judge** evaluation pattern
- **Long-term memory** — fact extraction and injection into system prompt
- **Webhook** deployment with aiohttp on Render

---

## Environment variables reference

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather |
| `WEBHOOK_HOST` | Your Render service URL (e.g. `https://your-bot.onrender.com`) |
| `BOT_PASSWORD` | Password to access the bot |
| `PORT` | Port for the web server (set automatically by Render, default 10000) |
