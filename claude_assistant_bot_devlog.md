# Dev Log: claude_assistant_bot

> Дневник разработки Telegram бота на базе Claude API.
> Цель: применить все темы курса "Building with the Claude API" и создать конспект-проект.

---

## Как вести этот дневник

- После каждого нового шага добавляй запись с датой
- Пиши кратко: что сделал, какие команды вводил, какие проблемы возникли и как решил
- Если что-то не работало — записывай причину и решение. Это самое ценное
- Не пиши весь код — только ключевые моменты и команды

**Структура записи:**
```
### Шаг N — Название
**Что сделал:** ...
**Команды:** ...
**Проблемы:** ...
**Решение:** ...
**Заметки:** ...
```

---

## Стек проекта

- Python 3.12
- aiogram 3 — Telegram бот
- anthropic — Claude API
- python-dotenv — переменные окружения
- uv — менеджер пакетов
- Render — хостинг
- GitHub — репозиторий

---

## История разработки

### Шаг 1 — Создание проекта в PyCharm
**Что сделал:** Создал новый проект в PyCharm, удалил стандартное виртуальное окружение.

**Команды:**
```bash
rm -rf .venv
uv init
```

**Заметки:** `uv init` автоматически создаёт `pyproject.toml`, `uv.lock` и `.gitignore` с `.venv` и `__pycache__`.

---

### Шаг 2 — Настройка .gitignore
**Что сделал:** Добавил в `.gitignore` дополнительные строки.

**Содержимое `.gitignore`:**
```
.venv
__pycache__
.env
.idea
```

**Заметки:** `.idea` — папка настроек PyCharm, не нужна в Git. `.env` — секретные ключи, никогда не пушить в репозиторий.

---

### Шаг 3 — Установка зависимостей
**Что сделал:** Установил все нужные библиотеки через uv.

**Команда:**
```bash
uv add anthropic aiogram python-dotenv
```

**Заметки:** uv автоматически обновляет `pyproject.toml` и `uv.lock`. Не нужен `requirements.txt`.

---

### Шаг 4 — Создание структуры папок
**Что сделал:** Создал папки и файлы проекта.

**Команды:**
```bash
mkdir bot claude tools
touch bot/__init__.py bot/handlers.py bot/config.py
touch claude/__init__.py claude/client.py claude/conversation.py
touch tools/__init__.py
touch main.py
```

**Структура проекта:**
```
claude_assistant_bot/
├── main.py              # точка входа
├── bot/
│   ├── __init__.py
│   ├── handlers.py      # обработчики команд Telegram
│   └── config.py        # настройки и переменные окружения
├── claude/
│   ├── __init__.py
│   ├── client.py        # базовый Anthropic клиент
│   └── conversation.py  # управление историей диалога
├── tools/
│   └── __init__.py      # инструменты (добавим позже)
├── .env                 # секретные ключи (не в Git!)
├── .gitignore
└── pyproject.toml
```

---

### Шаг 5 — Файл .env
**Что сделал:** Создал файл с секретными ключами.

**Содержимое `.env`:**
```
ANTHROPIC_API_KEY=твой_ключ
TELEGRAM_BOT_TOKEN=твой_токен
```

**Заметки:** Токен Telegram берётся у @BotFather. API ключ Anthropic — на console.anthropic.com.

---

### Шаг 6 — bot/config.py
**Что сделал:** Настройки проекта — модели, лимиты, переменные окружения.

**Ключевые моменты:**
- `load_dotenv()` загружает переменные из `.env`
- Две модели: Haiku (дешёвая, быстрая) и Sonnet (для сложных задач)
- `MAX_HISTORY = 20` — максимум сообщений в истории диалога (10 пар вопрос-ответ)
- `TEMPERATURE = 1` — стандартное значение для Claude

```python
CLAUDE_HAIKU = "claude-haiku-4-5-20251001"
CLAUDE_SONNET = "claude-sonnet-4-6"
MAX_TOKENS = 1024
TEMPERATURE = 1
MAX_HISTORY = 20
```

---

### Шаг 7 — claude/client.py
**Что сделал:** Базовый клиент для запросов к Claude API.

**Ключевые моменты:**
- `anthropic.Anthropic(api_key=...)` — создание клиента
- Функция `ask_claude(messages, system, model)` — универсальный запрос
- `messages` — список в формате `[{"role": "user", "content": "..."}]`
- `system` — системный промпт (необязательный)
- Ответ: `response.content[0].text`

---

### Шаг 8 — claude/conversation.py
**Что сделал:** Класс для управления историей диалога каждого пользователя.

**Ключевые моменты:**
- `ConversationManager` — класс с словарём `{user_id: [messages]}`
- Claude не помнит предыдущие сообщения сам — история передаётся каждый раз заново
- При превышении `MAX_HISTORY` старые сообщения обрезаются
- Методы: `add_message()`, `get_history()`, `clear_history()`

**Почему класс, а не функции:** состояние (histories) должно жить всё время работы бота.

---

### Шаг 9 — bot/handlers.py
**Что сделал:** Обработчики команд и сообщений Telegram на aiogram 3.

**Ключевые моменты:**
- `Router` — регистратор обработчиков (в aiogram 3 вместо глобального диспетчера)
- `@router.message(Command("start"))` — декоратор для команды
- `F.text` — фильтр для текстовых сообщений
- `async/await` — все обработчики асинхронные
- `send_chat_action("typing")` — индикатор печати пока Claude думает
- Системный промпт определяет поведение бота

**Порядок обработки сообщения:**
1. Получить user_id и текст
2. Добавить в историю
3. Отправить "typing..."
4. Запросить Claude с историей
5. Добавить ответ в историю
6. Отправить ответ пользователю

---

### Шаг 10 — main.py
**Что сделал:** Точка входа — запуск бота.

**Ключевые моменты:**
- `Bot(token=..., default=DefaultBotProperties(parse_mode=ParseMode.HTML))` — HTML разметка в сообщениях
- `Dispatcher` — главный обработчик событий
- `dp.include_router(router)` — подключение роутера из handlers.py
- `delete_webhook(drop_pending_updates=True)` — сброс вебхука перед polling
- `start_polling(bot)` — бот постоянно опрашивает Telegram
- `asyncio.run(main())` — запуск асинхронного кода

---

### Шаг 11 — Первый запуск
**Команда:**
```bash
uv run main.py
```

**Результат:**
```
INFO:__main__:Bot started
INFO:aiogram.dispatcher:Start polling
INFO:aiogram.dispatcher:Run polling for bot @... 
```

**Проверка:** бот ответил на `/start` и на текстовое сообщение через Claude. ✅

---

### Шаг 12 — claude/streaming.py
**Что сделал:** Стриминг ответов от Claude — текст приходит кусками по мере генерации.

**Ключевые моменты:**
- `stream_claude` — генератор (использует `yield`)
- `client.messages.stream()` — специальный метод SDK для стриминга
- `stream.text_stream` — итератор который выдаёт текст по кускам
- В `handlers.py` добавлена команда `/stream`
- Сообщение редактируется каждые 10 чанков — защита от rate limit Telegram
- На Haiku стриминг почти незаметен — модель слишком быстрая. Заметнее на Sonnet и длинных ответах.

---

### Шаг 13 — tools/notes_tool.py
**Что сделал:** Инструмент для работы с заметками — сохранение в JSON файл.

**Ключевые моменты:**
- Заметки хранятся в `notes.json` в корне проекта
- `_load_notes()` / `_save_notes()` — приватные функции (префикс `_`) для работы с файлом
- 4 публичных функции: `add_note()`, `get_note()`, `list_notes()`, `delete_note()`
- `"\n".join(f"- {title}" for title in notes.keys())` — генератор + join для форматирования списка в строку

---

### Шаг 14 — claude/tools.py + tool use
**Что сделал:** Подключил инструменты к Claude через tool use API.

**Ключевые моменты:**
- `NOTES_TOOLS` — список описаний инструментов в формате JSON Schema
- Каждый инструмент имеет `name`, `description`, `input_schema`
- `process_tool_call()` — диспетчер, вызывает нужную функцию по имени
- В `claude/client.py` добавлена функция `ask_claude_with_tools()`
- **Agentic loop** — цикл `while True` пока Claude вызывает инструменты:
  1. Отправить запрос с инструментами
  2. Если `stop_reason == "end_turn"` — вернуть ответ
  3. Если `stop_reason == "tool_use"` — выполнить инструмент, добавить результат, повторить
- В `handlers.py` добавлена команда `/note`
- Также добавлена функция `edit_note()` — редактирование заметки

---

### Шаг 15 — mcp_module/mcp_server.py + mcp_client.py
**Что сделал:** MCP сервер с инструментами и клиент для подключения к нему.

**Важно:** Папку назвал `mcp_module` (не `mcp`) — иначе конфликт с библиотекой `mcp`.

**Проблема:** При запуске сервер не видел модуль `tools`. 
**Решение:** Добавить путь к проекту в начало `mcp_server.py`:
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

**Ключевые моменты MCP сервера:**
- `@mcp.tool()` — инструменты для Claude
- `@mcp.resource()` — данные доступные по URI (`notes://all`)
- `@mcp.prompt()` — шаблоны промптов

**Ключевые моменты MCP клиента:**
- `StdioServerParameters` — запускает сервер как отдельный процесс
- `session.list_tools()` — получает список инструментов с сервера динамически
- `session.call_tool()` — вызывает инструмент на сервере
- Тот же agentic loop, но инструменты выполняются на отдельном процессе

**Разница `/note` vs `/mcp`:**
- `/note` — монолит, инструменты вызываются напрямую
- `/mcp` — MCP протокол, инструменты на отдельном процессе, можно подключить к любому MCP клиенту

**Установка:** `uv add mcp`

---

### Шаг 16 — RAG (rag/)
**Что сделал:** RAG пайплайн — ответы на вопросы по загруженным документам.

**Команда установки:**
```bash
uv add chromadb sentence-transformers
```

**Файлы:**
- `rag/embeddings.py` — создание векторов через `sentence-transformers` (модель `all-MiniLM-L6-v2`)
- `rag/vector_store.py` — хранение и поиск в ChromaDB
- `rag/retrieval.py` — RAG пайплайн

**Как работает RAG:**
1. `/upload текст` — текст превращается в вектор и сохраняется в ChromaDB
2. `/ask_with_rag вопрос` — вопрос превращается в вектор, ищем похожие документы
3. Найденные документы передаются Claude как контекст
4. Claude отвечает только на основе контекста

**Заметки:**
- Команда `/ask` переименована в `/ask_with_rag` для ясности
- При первом запуске `sentence-transformers` скачивает модель — занимает время
- ChromaDB сохраняет данные в папку `./chroma_db`
- Для ответов по документам используется `CLAUDE_SONNET` (точнее чем Haiku)

---

### Шаг 17 — Агентские workflows (workflows/)
**Что сделал:** Три типа агентских цепочек.

**Файлы:**
- `workflows/chains.py` — sequential chain (перевод → суммаризация → форматирование)
- `workflows/parallel.py` — параллельный анализ текста с трёх сторон одновременно
- `workflows/routing.py` — автоматический роутинг запроса к нужному обработчику

**Команды бота:** `/chain`, `/parallel`, `/route`

**Ключевые моменты:**
- **Chain** — вывод одного шага становится входом следующего
- **Parallel** — `asyncio.gather()` + `loop.run_in_executor()` для параллельных запросов к Claude
- **Routing** — Claude сначала классифицирует запрос (QUESTION/TRANSLATION/SUMMARY/CODE), потом отвечает с нужным системным промптом

---

### Шаг 18 — Structured outputs (claude/structured.py)
**Что сделал:** Получение структурированных JSON ответов от Claude.

**Команды бота:** `/sentiment`, `/tasks`

**Ключевые моменты:**
- `get_structured_response()` — просит Claude вернуть строго JSON по схеме
- Очищает ответ от markdown тройных кавычек перед `json.loads()`
- `analyze_sentiment()` — анализ тональности текста
- `extract_tasks()` — извлечение задач с приоритетами из текста
- В handlers используется явный `parse_mode="HTML"` — так форматирование работает надёжнее

---

### Шаг 19 — Тесты и эвалы (evals/)
**Что сделал:** Тестирование качества и скорости ответов Claude.

**Файлы:**
- `evals/test_prompts.py` — Claude оценивает сам себя по критериям (LLM-as-a-judge)
- `evals/benchmarks.py` — замер времени ответа Haiku vs Sonnet

**Команды бота:** `/test`, `/benchmark`

**Результаты benchmark:**
- Haiku: ~1.09s avg
- Sonnet: ~2.26s avg (в 2 раза медленнее но точнее)

**Разница между файлами:**
- `test_prompts.py` — проверяет **качество** (точность, краткость, правильность)
- `benchmarks.py` — проверяет **скорость** (время ответа, стабильность)

---

### Шаг 20 — Модуль долгосрочной памяти (memory/)
**Что сделал:** Долгосрочная память — сохранение важных фактов о пользователе между сессиями.

**Файлы:**
- `memory/memory_store.py` — хранение фактов в `memory.json`
- `memory/memory_manager.py` — извлечение фактов из сообщений и инжекция в системный промпт

**Команды бота:** `/memory`, `/forget`

**Ключевые моменты:**
- `extract_and_save_facts()` — Claude анализирует каждое сообщение и извлекает важные факты (имя, профессия, интересы)
- Факты сохраняются в `memory.json` по `user_id`
- `build_memory_prompt()` — формирует строку с фактами для системного промпта
- `ask_claude_with_memory()` — обычный запрос но с памятью в системном промпте
- `handle_message` обновлён — теперь использует память

---

### Шаг 21 — MCP Advanced: Sampling
**Что сделал:** Сервер делает запрос к Claude через клиента — демонстрация sampling.

**Команда бота:** `/summarize_note`

**Ключевые моменты:**
- Sampling — сервер просит клиента сгенерировать текст через Claude
- `ctx.session.create_message()` — низкоуровневый вызов sampling
- `Context` инжектируется в функцию как параметр — официальный способ FastMCP
- `system_prompt` передаётся в sampling запрос
- Клиент должен поддерживать sampling — нужен `sampling_callback` в `ClientSession`

**Проблема мультиязычности в sampling:**
- `system_prompt` и инструкции языка игнорируются в sampling
- Решение — передавать язык как явный параметр инструмента:
```python
async def tool_summarize_note_with_sampling(title: str, language: str, ctx: Context)
```
Claude сам определяет язык из контекста и передаёт его в инструмент.

---

### Шаг 22 — MCP Advanced: Log and progress notifications
**Что сделал:** Сервер отправляет уведомления о прогрессе клиенту.

**Команда бота:** `/process_notes`

**Ключевые моменты:**
- `ctx.info()` — отправить лог сообщение
- `ctx.report_progress(current, total)` — отправить прогресс
- Notifications видны только в логах сервера — не в Telegram
- Это инструмент для разработчика, не для конечного пользователя

---

### Шаг 23 — MCP Advanced: Roots
**Что сделал:** Клиент сообщает серверу к каким директориям он имеет доступ.

**Команда бота:** `/roots`

**Ключевые моменты:**
- Roots — список разрешённых директорий, которые клиент передаёт серверу
- В mcp 1.27.0 roots передаются через `list_roots_callback` в `ClientSession`
- Callback должен возвращать `ListRootsResult`, не просто список
- Сервер запрашивает roots через `ctx.session.list_roots()`

**Проблема:** В старых версиях `ClientSession` принимал `roots` как параметр — в 1.27.0 это изменилось на callback.

---

### Шаг 24 — MCP Advanced: StreamableHTTP transport
**Что сделал:** HTTP сервер для продакшена вместо STDIO.

**Файлы:**
- `mcp_module/mcp_server_http.py` — HTTP сервер с `stateless_http=True, json_response=True`
- `mcp_module/mcp_client_http.py` — HTTP клиент

**Команда бота:** `/mcp_http`

**Установка:**
```bash
uv add uvicorn
```

**Запуск HTTP сервера:**
```bash
uv run python mcp_module/mcp_server_http.py
```

**Ключевые моменты:**
- `stateless_http=True` — нет состояния между запросами, подходит для serverless
- `json_response=True` — ответы в JSON вместо SSE
- `streamable_http_client` (не `streamablehttp_client`) — правильное название в mcp 1.27.0
- STDIO — для локальной разработки. HTTP — для продакшена
- На Render: бот и MCP HTTP сервер деплоятся как два отдельных сервиса

---

## Все шаги проекта

- [x] Создание проекта в PyCharm + uv init
- [x] Настройка .gitignore
- [x] Установка зависимостей
- [x] Создание структуры папок
- [x] Файл .env
- [x] bot/config.py
- [x] claude/client.py
- [x] claude/conversation.py
- [x] bot/handlers.py
- [x] main.py — точка входа
- [x] Первый запуск
- [x] Streaming — claude/streaming.py
- [x] Tool use — tools/notes_tool.py
- [x] Tool use — claude/tools.py + ask_claude_with_tools()
- [x] MCP сервер — mcp_module/mcp_server.py + mcp_client.py
- [x] RAG — rag/embeddings.py + vector_store.py + retrieval.py
- [x] Агентские workflows — chains, parallel, routing
- [x] Structured outputs — claude/structured.py
- [x] Тесты и эвалы — evals/test_prompts.py + benchmarks.py
- [x] Модуль долгосрочной памяти (memory)
- [x] MCP Advanced — sampling
- [x] MCP Advanced — log and progress notifications
- [x] MCP Advanced — roots
- [x] MCP Advanced — StreamableHTTP transport
- [ ] Клавиатура с кнопками для всех команд
- [ ] Исправить HTML форматирование в обычных сообщениях
- [ ] Деплой на Render + GitHub (бот + MCP HTTP сервер как отдельный сервис)
