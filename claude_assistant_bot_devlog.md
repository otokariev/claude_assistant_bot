# Dev Log: claude_assistant_bot

> Development diary of a Telegram bot powered by Claude API.
> Goal: apply all topics from the "Building with the Claude API" course and create a reference project.

---

## How to use this diary

- After each new step, add an entry with the date
- Write briefly: what you did, which commands you ran, what problems occurred and how you solved them
- If something didn't work — write down the cause and the solution. That's the most valuable part
- Don't write all the code — only key moments and commands

**Entry structure:**
```
### Step N — Title
**What I did:** ...
**Commands:** ...
**Problems:** ...
**Solution:** ...
**Notes:** ...
```

---

## Tech stack

- Python 3.12
- aiogram 3 — Telegram bot framework
- anthropic — Claude API
- python-dotenv — environment variables
- uv — package manager
- Render — hosting
- GitHub — repository

---

## Development history

### Step 1 — Project setup in PyCharm
**What I did:** Created a new project in PyCharm, removed the default virtual environment.

**Commands:**
```bash
rm -rf .venv
uv init
```

**Notes:** `uv init` automatically creates `pyproject.toml`, `uv.lock` and `.gitignore` with `.venv` and `__pycache__`.

---

### Step 2 — Configure .gitignore
**What I did:** Added extra entries to `.gitignore`.

**Contents of `.gitignore`:**
```
.venv
__pycache__
.env
.idea
```

**Notes:** `.idea` is the PyCharm settings folder — not needed in Git. `.env` contains secret keys — never push to repository.

---

### Step 3 — Install dependencies
**What I did:** Installed all required libraries via uv.

**Command:**
```bash
uv add anthropic aiogram python-dotenv
```

**Notes:** uv automatically updates `pyproject.toml` and `uv.lock`. No `requirements.txt` needed.

---

### Step 4 — Create project structure
**What I did:** Created folders and files for the project.

**Commands:**
```bash
mkdir bot claude tools
touch bot/__init__.py bot/handlers.py bot/config.py
touch claude/__init__.py claude/client.py claude/conversation.py
touch tools/__init__.py
touch main.py
```

**Project structure:**
```
claude_assistant_bot/
├── main.py              # entry point
├── bot/
│   ├── __init__.py
│   ├── handlers.py      # Telegram command handlers
│   └── config.py        # settings and environment variables
├── claude/
│   ├── __init__.py
│   ├── client.py        # base Anthropic client
│   └── conversation.py  # conversation history manager
├── tools/
│   └── __init__.py      # tools (added later)
├── .env                 # secret keys (not in Git!)
├── .gitignore
└── pyproject.toml
```

---

### Step 5 — .env file
**What I did:** Created a file with secret keys.

**Contents of `.env`:**
```
ANTHROPIC_API_KEY=your_key
TELEGRAM_BOT_TOKEN=your_token
```

**Notes:** Telegram token is obtained from @BotFather. Anthropic API key — at console.anthropic.com.

---

### Step 6 — bot/config.py
**What I did:** Project settings — models, limits, environment variables.

**Key points:**
- `load_dotenv()` loads variables from `.env`
- Two models: Haiku (cheap, fast) and Sonnet (for complex tasks)
- `MAX_HISTORY = 20` — max messages in conversation history (10 question-answer pairs)
- `TEMPERATURE = 1` — standard value for Claude
- `MULTILINGUAL_INSTRUCTION` — constant to make Claude respond in the user's language

```python
CLAUDE_HAIKU = "claude-haiku-4-5-20251001"
CLAUDE_SONNET = "claude-sonnet-4-6"
MAX_TOKENS = 1024
TEMPERATURE = 1
MAX_HISTORY = 20
MULTILINGUAL_INSTRUCTION = "Always respond in the same language as the user's message."
```

---

### Step 7 — claude/client.py
**What I did:** Base client for Claude API requests.

**Key points:**
- `anthropic.Anthropic(api_key=...)` — creates the client
- Function `ask_claude(messages, system, model)` — universal request
- `messages` — list in format `[{"role": "user", "content": "..."}]`
- `system` — system prompt (optional)
- Response: `response.content[0].text`

---

### Step 8 — claude/conversation.py
**What I did:** Class for managing conversation history per user.

**Key points:**
- `ConversationManager` — class with dict `{user_id: [messages]}`
- Claude doesn't remember previous messages itself — history is sent every time
- When `MAX_HISTORY` is exceeded, old messages are trimmed
- Methods: `add_message()`, `get_history()`, `clear_history()`

**Why a class and not functions:** state (histories) must live for the entire bot lifetime.

---

### Step 9 — bot/handlers.py
**What I did:** Telegram command and message handlers using aiogram 3.

**Key points:**
- `Router` — handler registrar (replaces global dispatcher in aiogram 3)
- `@router.message(Command("start"))` — decorator for a command
- `F.text` — filter for text messages
- `async/await` — all handlers are asynchronous
- `send_chat_action("typing")` — typing indicator while Claude is thinking
- System prompt defines bot behavior

**Message processing order:**
1. Get user_id and text
2. Add to history
3. Send "typing..."
4. Request Claude with history
5. Add response to history
6. Send response to user

---

### Step 10 — main.py
**What I did:** Entry point — bot startup.

**Key points:**
- `Bot(token=..., default=DefaultBotProperties(parse_mode=ParseMode.HTML))` — HTML markup in messages
- `Dispatcher` — main event handler
- `dp.include_router(router)` — connects router from handlers.py
- `delete_webhook(drop_pending_updates=True)` — resets webhook before polling
- `start_polling(bot)` — bot constantly polls Telegram
- `asyncio.run(main())` — starts async code

---

### Step 11 — First run
**Command:**
```bash
uv run main.py
```

**Result:**
```
INFO:__main__:Bot started
INFO:aiogram.dispatcher:Start polling
INFO:aiogram.dispatcher:Run polling for bot @...
```

**Check:** bot responded to `/start` and to a text message via Claude. ✅

---

### Step 12 — claude/streaming.py
**What I did:** Streaming responses from Claude — text arrives in chunks as it generates.

**Key points:**
- `stream_claude` — generator (uses `yield`)
- `client.messages.stream()` — special SDK method for streaming
- `stream.text_stream` — iterator that yields text in chunks
- `/stream` command added to `handlers.py`
- Message is edited every 10 chunks — protection against Telegram rate limit
- On Haiku streaming is barely noticeable — model is too fast. More visible on Sonnet and long responses.

---

### Step 13 — tools/notes_tool.py
**What I did:** Tool for working with notes — saving to JSON file.

**Key points:**
- Notes are stored in `notes.json` in the project root
- `_load_notes()` / `_save_notes()` — private functions (prefix `_`) for file operations
- 5 public functions: `add_note()`, `get_note()`, `list_notes()`, `delete_note()`, `edit_note()`
- `"\n".join(f"- {title}" for title in notes.keys())` — generator + join to format list as string
- Absolute path used to avoid path conflicts when MCP server runs as subprocess:
```python
NOTES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notes.json")
```

---

### Step 14 — claude/tools.py + tool use
**What I did:** Connected tools to Claude via tool use API.

**Key points:**
- `NOTES_TOOLS` — list of tool descriptions in JSON Schema format
- Each tool has `name`, `description`, `input_schema`
- `process_tool_call()` — dispatcher, calls the right function by name
- `ask_claude_with_tools()` added to `claude/client.py`
- **Agentic loop** — `while True` loop while Claude calls tools:
  1. Send request with tools
  2. If `stop_reason == "end_turn"` — return response
  3. If `stop_reason == "tool_use"` — execute tool, add result, repeat
- `/note` command added to `handlers.py`

**Important:** Tool description affects Claude's behavior. If Claude uses the wrong tool, make the description more explicit:
```python
"description": "Get a list of ALL saved notes. Always use this tool when user asks to show, list or view all notes."
```

---

### Step 15 — mcp_module/mcp_server.py + mcp_client.py
**What I did:** MCP server with tools and client for connecting to it.

**Important:** Folder named `mcp_module` (not `mcp`) — otherwise conflict with the `mcp` library.

**Problem:** Server couldn't find the `tools` module when launched as a subprocess.
**Solution:** Add project path to the beginning of `mcp_server.py`:
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

**Key points about MCP server:**
- `@mcp.tool()` — tools for Claude
- `@mcp.resource()` — data accessible by URI (`notes://all`)
- `@mcp.prompt()` — prompt templates

**Key points about MCP client:**
- `StdioServerParameters` — launches server as a separate process
- `session.list_tools()` — gets list of tools from server dynamically
- `session.call_tool()` — calls a tool on the server
- Same agentic loop, but tools execute on a separate process

**Difference `/note` vs `/mcp`:**
- `/note` — monolith, tools called directly
- `/mcp` — MCP protocol, tools on separate process, can connect to any MCP client

**Installation:** `uv add mcp`

---

### Step 16 — RAG (rag/)
**What I did:** RAG pipeline — answers to questions based on uploaded documents.

**Installation:**
```bash
uv add chromadb sentence-transformers
```

**Files:**
- `rag/embeddings.py` — vector generation via `sentence-transformers` (model `all-MiniLM-L6-v2`)
- `rag/vector_store.py` — storage and search in ChromaDB
- `rag/retrieval.py` — RAG pipeline

**How RAG works:**
1. `/upload text` — text is converted to a vector and saved in ChromaDB
2. `/ask_with_rag question` — question is converted to vector, similar documents are found
3. Found documents are passed to Claude as context
4. Claude answers based only on the context

**Notes:**
- Command `/ask` renamed to `/ask_with_rag` for clarity
- On first run `sentence-transformers` downloads the model — takes time
- ChromaDB saves data to `./chroma_db` folder
- `CLAUDE_SONNET` used for document answers (more accurate than Haiku)
- RAG imports moved to lazy imports inside handler functions to speed up server startup

---

### Step 17 — Agentic workflows (workflows/)
**What I did:** Three types of agentic chains.

**Files:**
- `workflows/chains.py` — sequential chain (translate → summarize → format as bullet points)
- `workflows/parallel.py` — parallel text analysis from three angles simultaneously
- `workflows/routing.py` — automatic request routing to the right handler

**Bot commands:** `/chain`, `/parallel`, `/route`

**Key points:**
- **Chain** — output of one step becomes input of the next
- **Parallel** — `asyncio.gather()` + `loop.run_in_executor()` for parallel Claude requests
- **Routing** — Claude first classifies the request (QUESTION/TRANSLATION/SUMMARY/CODE), then responds with the right system prompt

---

### Step 18 — Structured outputs (claude/structured.py)
**What I did:** Getting structured JSON responses from Claude.

**Bot commands:** `/sentiment`, `/tasks`

**Key points:**
- `get_structured_response()` — asks Claude to return strictly JSON by schema
- Cleans response from markdown triple backticks before `json.loads()`
- `analyze_sentiment()` — text sentiment analysis
- `extract_tasks()` — extracting tasks with priorities from text
- Explicit `parse_mode="HTML"` used in handlers — more reliable formatting

---

### Step 19 — Tests and evals (evals/)
**What I did:** Testing quality and speed of Claude responses.

**Files:**
- `evals/test_prompts.py` — Claude evaluates itself by criteria (LLM-as-a-judge)
- `evals/benchmarks.py` — response time measurement Haiku vs Sonnet

**Bot commands:** `/test`, `/benchmark`

**Benchmark results:**
- Haiku: ~1.09s avg
- Sonnet: ~2.26s avg (2x slower but more accurate)

**Difference between files:**
- `test_prompts.py` — checks **quality** (accuracy, conciseness, correctness)
- `benchmarks.py` — checks **speed** (response time, stability)

---

### Step 20 — Long-term memory module (memory/)
**What I did:** Long-term memory — saving important facts about the user between sessions.

**Files:**
- `memory/memory_store.py` — storing facts in `memory.json`
- `memory/memory_manager.py` — extracting facts from messages and injecting into system prompt

**Bot commands:** `/memory`, `/forget`

**Key points:**
- `extract_and_save_facts()` — Claude analyzes each message and extracts important facts (name, profession, interests)
- Facts saved in `memory.json` by `user_id`
- `build_memory_prompt()` — builds a string with facts for the system prompt
- `ask_claude_with_memory()` — regular request but with memory in system prompt
- `handle_message` updated — now uses memory

---

### Step 21 — MCP Advanced: Sampling
**What I did:** Server makes a request to Claude via the client — demonstrates sampling.

**Bot command:** `/summarize_note`

**Key points:**
- Sampling — server asks client to generate text via Claude
- `ctx.session.create_message()` — low-level sampling call
- `Context` is injected into the function as a parameter — official FastMCP way
- `system_prompt` is passed in the sampling request
- Client must support sampling — `sampling_callback` needed in `ClientSession`

**Multilingual problem in sampling:**
- `system_prompt` and language instructions are ignored in sampling
- Solution — pass language as an explicit tool parameter:
```python
async def tool_summarize_note_with_sampling(title: str, language: str, ctx: Context)
```
Claude determines the language from context and passes it to the tool.

---

### Step 22 — MCP Advanced: Log and progress notifications
**What I did:** Server sends progress notifications to the client.

**Bot command:** `/process_notes`

**Key points:**
- `ctx.info()` — send log message
- `ctx.report_progress(current, total)` — send progress
- Notifications are visible only in server logs — not in Telegram
- This is a developer tool, not for end users

---

### Step 23 — MCP Advanced: Roots
**What I did:** Client tells the server which directories it has access to.

**Bot command:** `/roots`

**Key points:**
- Roots — list of allowed directories that client passes to server
- In mcp 1.27.0 roots are passed via `list_roots_callback` in `ClientSession`
- Callback must return `ListRootsResult`, not just a list
- Server requests roots via `ctx.session.list_roots()`

**Problem:** In older versions `ClientSession` accepted `roots` as a parameter — in 1.27.0 this changed to a callback.

---

### Step 24 — MCP Advanced: StreamableHTTP transport
**What I did:** HTTP server for production instead of STDIO.

**Files:**
- `mcp_module/mcp_server_http.py` — HTTP server with `stateless_http=True, json_response=True`
- `mcp_module/mcp_client_http.py` — HTTP client

**Bot command:** `/mcp_http`

**Installation:**
```bash
uv add uvicorn
```

**Start HTTP server:**
```bash
uv run python mcp_module/mcp_server_http.py
```

**Key points:**
- `stateless_http=True` — no state between requests, suitable for serverless
- `json_response=True` — responses in JSON instead of SSE
- `streamable_http_client` (not `streamablehttp_client`) — correct name in mcp 1.27.0
- STDIO — for local development. HTTP — for production
- On Render: bot and MCP HTTP server deploy as two separate services

---

### Step 25 — Keyboard with buttons for all commands
**What I did:** Created a reply keyboard with all bot commands for easier navigation.

**File:** `bot/keyboard.py`

**Key points:**
- `ReplyKeyboardMarkup` — persistent keyboard shown below the message input
- `KeyboardButton` — each button sends the command text when tapped
- `resize_keyboard=True` — keyboard adapts to screen size
- `input_field_placeholder` — hint text in the message input field
- Buttons arranged in 2 per row for compact display
- `/start` button removed — Telegram shows it automatically on first open

**How to connect:**
- Import `get_main_keyboard` in `handlers.py`
- Pass `reply_markup=get_main_keyboard()` to `cmd_start`
- Keyboard appears after user sends `/start`

---

### Step 26 — Fix HTML formatting in regular messages
**What I did:** Made Claude respond with HTML formatting instead of Markdown.

**Problem:** `ParseMode.HTML` was set in `main.py`, but Claude was returning Markdown (`**bold**`, `*italic*`). Telegram was displaying raw asterisks instead of formatted text.

**Solution:**
- Added HTML formatting instruction to `SYSTEM_PROMPT` in `handlers.py`:
```python
SYSTEM_PROMPT = f"""You are a helpful assistant in Telegram.
Answer concisely and clearly.
Use HTML formatting: <b>bold</b>, <i>italic</i>, <code>code</code>. Never use markdown.
{MULTILINGUAL_INSTRUCTION}"""
```
- Added same instruction to system prompt in `handle_note`
- For handlers that need formatting, explicit `parse_mode="HTML"` passed:
```python
await message.answer(response, parse_mode="HTML")
```

**Notes:**
- `ParseMode.HTML` is more reliable than `MARKDOWN_V2` — no need to escape special characters
- Claude sometimes ignores formatting instructions — explicit `parse_mode` in each handler is the safest approach

---

### Step 27 — GitHub
**What I did:** Configured git and created a GitHub repository.

**Commands:**
```bash
git config --global user.name "name"
git config --global user.email "email"
sudo dnf install gh
gh auth login
```

**Added to `.gitignore`:**
```
chroma_db/
notes.json
memory.json
```

**Create repository and first push:**
```bash
git add .
git commit -m "Initial commit: Claude Assistant Bot"
gh repo create claude_assistant_bot --public --source=. --remote=origin --push
```

**Notes:**
- `gh` — GitHub CLI, official utility for working with GitHub from the terminal
- `--public` — public repository, replace with `--private` for private
- `38 files changed, 5467 insertions` — most of it is `uv.lock`, actual code ~500-800 lines

---

### Step 28 — Prepare for deployment: switch to webhook
**What I did:** Replaced polling with webhook in `main.py` for Render deployment.

**Installation:**
```bash
uv add aiohttp
```

**Key points:**
- Polling on free Render sleeps after 15 minutes — bot stops responding
- Webhook — Telegram sends updates to URL itself, service doesn't sleep
- `WEBHOOK_HOST` — Render service URL (environment variable)
- `PORT` — port provided by Render (env variable, default 10000)
- `web.run_app()` replaces `asyncio.run()` — creates event loop itself
- `on_startup` — sets webhook on startup

**Environment variables for Render:**
```
TELEGRAM_BOT_TOKEN=...
ANTHROPIC_API_KEY=...
WEBHOOK_HOST=https://your-service.onrender.com
BOT_PASSWORD=...
```

---

### Step 29 — Fix webhook after deployment
**Problem:** After every redeploy the webhook was lost — URL became empty and bot stopped responding.

**Cause:** Race condition during redeploy:
1. New process starts and sets webhook via `dp.startup.register(on_startup)`
2. Old process terminates and calls `on_shutdown` which deletes webhook
3. Result: webhook is empty

**Step-by-step solution:**
1. Removed `on_shutdown` — webhook doesn't need to be deleted on shutdown
2. Moved webhook setup from aiogram lifecycle to aiohttp lifecycle:
```python
# Before (aiogram):
dp.startup.register(on_startup)

# After (aiohttp):
app["bot"] = bot
app.on_startup.append(on_startup)

async def on_startup(app):
    await app["bot"].set_webhook(WEBHOOK_URL, drop_pending_updates=True)
```
3. Added error handling in `on_startup`

**Why aiohttp lifecycle is better:**
- Executes earlier in the startup cycle
- Doesn't conflict with old process termination
- Webhook is guaranteed to be set before accepting requests

**Check webhook:**
```
https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```
If `url` is empty — set manually:
```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://claude-assistant-bot.onrender.com/webhook
```

---

### Step 30 — Password protection for the bot
**Why:** Bot uses paid Anthropic API — protection from unauthorized users needed. User's API key is not used (nobody will enter their own key into someone else's bot).

**How it works step by step:**
1. User sends `/start`
2. If not authorized — bot asks for password
3. User enters password
4. If correct — authorization saved in `memory.json`, keyboard appears
5. If wrong — bot asks to try again
6. On next sessions authorization is remembered — password not needed again

**Where password is stored:**
- In `.env` locally: `BOT_PASSWORD=your_password`
- On Render in Environment Variables: `BOT_PASSWORD=your_password`

**Code changes:**
- `bot/config.py` — added constant `BOT_PASSWORD`
- `memory/memory_store.py` — added functions `is_authorized()` and `authorize_user()`
- `bot/handlers.py` — `handle_message` replaced with `handle_password` with authorization check

**Notes:**
- Authorization stored in `memory.json` — resets if file is deleted
- `os.getenv("BOT_PASSWORD", "mypassword")` — default value in case variable is not set
- Don't forget to add `BOT_PASSWORD` to environment variables on Render!

---

### Step 31 — Deploy bot to Render
**Service settings:**
- Name: `claude-assistant-bot`
- Region: Frankfurt
- Branch: `master`
- Runtime: Python
- Build Command: `uv sync --frozen && uv cache prune --ci` (default)
- Start Command: `uv run main.py`
- Instance Type: Free

**Environment variables:**
```
TELEGRAM_BOT_TOKEN=...
ANTHROPIC_API_KEY=...
WEBHOOK_HOST=https://claude-assistant-bot.onrender.com
BOT_PASSWORD=...
```

**Problem during deployment:**
Render didn't see an open port — service failed with `Port scan timeout`. Cause — slow initialization of `sentence-transformers` and `chromadb`.

**Solution:**
- Port changed to 10000 (standard for Render)
- RAG modules moved to lazy imports inside handler functions

**UptimeRobot:**
- Free Render plan sleeps after 15 minutes without traffic
- UptimeRobot pings `/health` every 5 minutes — service stays awake
- Endpoint added to `main.py`:
```python
async def health_check(request):
    return web.Response(text="OK")
app.router.add_get("/health", health_check)
```
- URL for UptimeRobot: `https://claude-assistant-bot.onrender.com/health`

---

## All project steps

01. - [x] Project setup in PyCharm + uv init
02. - [x] Configure .gitignore
03. - [x] Install dependencies
04. - [x] Create project structure
05. - [x] .env file
06. - [x] bot/config.py
07. - [x] claude/client.py
08. - [x] claude/conversation.py
09. - [x] bot/handlers.py
10. - [x] main.py — entry point 
11. - [x] First run
12. - [x] Streaming — claude/streaming.py
13. - [x] Tool use — tools/notes_tool.py
14. - [x] Tool use — claude/tools.py + ask_claude_with_tools()
15. - [x] MCP server — mcp_module/mcp_server.py + mcp_client.py
16. - [x] RAG — rag/embeddings.py + vector_store.py + retrieval.py
17. - [x] Agentic workflows — chains, parallel, routing
18. - [x] Structured outputs — claude/structured.py
19. - [x] Tests and evals — evals/test_prompts.py + benchmarks.py
20. - [x] Long-term memory module (memory)
21. - [x] MCP Advanced — sampling
22. - [x] MCP Advanced — log and progress notifications
23. - [x] MCP Advanced — roots
24. - [x] MCP Advanced — StreamableHTTP transport
25. - [x] Keyboard with buttons for all commands
26. - [x] Fix HTML formatting in regular messages
27. - [x] GitHub — create repository
28. - [x] Prepare for deployment — switch to webhook
29. - [x] Fix webhook after deployment
30. - [x] Password protection for the bot
31. - [x] Deploy bot to Render