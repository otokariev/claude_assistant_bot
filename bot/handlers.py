from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from claude.conversation import ConversationManager
from claude.streaming import stream_claude
from claude.client import ask_claude_with_tools

from mcp_module.mcp_client import run_mcp_agent

from workflows.chains import run_chain
from workflows.parallel import run_parallel
from workflows.routing import route_request

from claude.structured import analyze_sentiment, extract_tasks

from evals.test_prompts import run_prompt_tests
from evals.benchmarks import run_benchmarks

from memory.memory_manager import extract_and_save_facts, ask_claude_with_memory
from memory.memory_store import get_facts, clear_facts

from bot.config import MULTILINGUAL_INSTRUCTION

from mcp_module.mcp_client_http import run_mcp_http_agent

from bot.keyboard import get_main_keyboard

router = Router()
conversation_manager = ConversationManager()

SYSTEM_PROMPT = f"""You are a helpful assistant in Telegram.
Answer concisely and clearly.
Use HTML formatting: <b>bold</b>, <i>italic</i>, <code>code</code>. Never use markdown.
{MULTILINGUAL_INSTRUCTION}"""


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    await message.answer(
        "Hello! I am your Claude assistant.\n\n"
        "Commands:\n"
        "/start - start\n"
        "/help - help\n"
        "/clear - clear conversation history",
        reply_markup=get_main_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    await message.answer(
        "I am a Claude-powered assistant.\n\n"
        "Just write me a message and I will answer.\n\n"
        "<b>Commands:</b>\n"
        "/clear - clear conversation history\n"
        "/stream - stream response word by word\n"
        "/note - manage notes\n"
        "/mcp - notes via MCP server\n"
        "/upload - add document to knowledge base\n"
        "/ask_with_rag - ask question about documents\n"
        "/chain - sequential chain workflow\n"
        "/parallel - parallel analysis\n"
        "/route - automatic request routing\n"
        "/sentiment - analyze text sentiment\n"
        "/tasks - extract tasks from text\n"
        "/test - run prompt quality tests\n"
        "/benchmark - benchmark model speed\n"
        "/memory - show what I remember about you\n"
        "/forget - clear my memory about you",
        parse_mode="HTML"
    )


@router.message(Command("clear"))
async def cmd_clear(message: Message):
    """Handle /clear command."""
    conversation_manager.clear_history(message.from_user.id)
    await message.answer("Conversation history cleared.")


@router.message(Command("stream"))
async def handle_stream(message: Message):
    """Handle /stream command - response streams word by word."""
    user_id = message.from_user.id
    # Get text after /stream command
    user_text = message.text.replace("/stream", "").strip()

    if not user_text:
        await message.answer("Write a message after /stream command.\nExample: /stream explain what is AI")
        return

    # Add user message to history
    conversation_manager.add_message(user_id, "user", user_text)
    history = conversation_manager.get_history(user_id)

    # Send initial empty message to edit later
    sent_message = await message.answer("...")

    # Collect streamed response and update message
    full_response = ""
    chunk_counter = 0

    for chunk in stream_claude(messages=history, system=SYSTEM_PROMPT):
        full_response += chunk
        chunk_counter += 1

        # Update message every 10 chunks to avoid Telegram rate limits
        if chunk_counter % 10 == 0:
            await sent_message.edit_text(full_response)

    # Send final complete response
    await sent_message.edit_text(full_response)

    # Add assistant response to history
    conversation_manager.add_message(user_id, "assistant", full_response)


@router.message(Command("note"))
async def handle_note(message: Message):
    """Handle /note command - Claude can save, get, list and delete notes."""
    user_id = message.from_user.id
    user_text = message.text.replace("/note", "").strip()

    if not user_text:
        await message.answer(
            "Write a request after /note command.\n"
            "Examples:\n"
            "/note save note 'Shopping' - buy milk, eggs, bread\n"
            "/note show note Shopping\n"
            "/note list all notes\n"
            "/note delete note Shopping"
        )
        return

    conversation_manager.add_message(user_id, "user", user_text)
    history = conversation_manager.get_history(user_id)

    await message.bot.send_chat_action(message.chat.id, "typing")

    response = ask_claude_with_tools(
        messages=history,
        system=f"You are a helpful assistant that manages user notes. "
               f"Use the available tools to save, retrieve, list and delete notes. "
               f"Always confirm what action you performed. "
               f"Use HTML formatting: <b>bold</b>, <i>italic</i>. Never use markdown. "
               f"{MULTILINGUAL_INSTRUCTION}"
    )

    conversation_manager.add_message(user_id, "assistant", response)
    await message.answer(response)


@router.message(Command("mcp"))
async def handle_mcp(message: Message):
    """Handle /mcp command - uses MCP server tools."""
    user_id = message.from_user.id
    user_text = message.text.replace("/mcp", "").strip()

    if not user_text:
        await message.answer(
            "Write a request after /mcp command.\n"
            "Examples:\n"
            "/mcp save note 'Ideas' - learn RAG\n"
            "/mcp show all notes\n"
            "/mcp delete note Ideas"
        )
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    response = await run_mcp_agent(user_text)

    conversation_manager.add_message(user_id, "assistant", response)
    await message.answer(response)


@router.message(Command("upload"))
async def handle_upload(message: Message):
    from rag.vector_store import add_document, get_collection_count
    """Handle /upload command - add text document to vector store."""
    user_text = message.text.replace("/upload", "").strip()

    if not user_text:
        await message.answer(
            "Write text after /upload command to add it to the knowledge base.\n"
            "Example: /upload Python is a high-level programming language created by Guido van Rossum."
        )
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    # Use message id as unique document id
    doc_id = f"doc_{message.message_id}"
    add_document(
        doc_id=doc_id,
        text=user_text,
        metadata={"user_id": message.from_user.id, "source": "telegram"}
    )

    count = get_collection_count()
    await message.answer(
        f"Document added to knowledge base.\n"
        f"Total documents: {count}"
    )


@router.message(Command("ask_with_rag"))
async def handle_ask_with_rag(message: Message):
    from rag.retrieval import answer_with_rag
    """Handle /ask_with_rag command - answer question using RAG."""
    user_text = message.text.replace("/ask_with_rag", "").strip()

    if not user_text:
        await message.answer(
            "Write a question after /ask_with_rag command.\n"
            "Example: /ask_with_rag what is Python?"
        )
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    response = answer_with_rag(user_text)
    await message.answer(response)


@router.message(Command("chain"))
async def handle_chain(message: Message):
    """Handle /chain command - sequential chain workflow."""
    user_text = message.text.replace("/chain", "").strip()

    if not user_text:
        await message.answer(
            "Write text after /chain command.\n"
            "Example: /chain Artificial intelligence is transforming the world."
        )
        return

    await message.bot.send_chat_action(message.chat.id, "typing")
    response = run_chain(user_text)
    await message.answer(response)


@router.message(Command("parallel"))
async def handle_parallel(message: Message):
    """Handle /parallel command - parallel analysis workflow."""
    user_text = message.text.replace("/parallel", "").strip()

    if not user_text:
        await message.answer(
            "Write text after /parallel command.\n"
            "Example: /parallel Artificial intelligence is transforming the world."
        )
        return

    await message.bot.send_chat_action(message.chat.id, "typing")
    response = await run_parallel(user_text)
    await message.answer(response)


@router.message(Command("route"))
async def handle_route(message: Message):
    """Handle /route command - automatic request routing workflow."""
    user_text = message.text.replace("/route", "").strip()

    if not user_text:
        await message.answer(
            "Write a request after /route command.\n"
            "Examples:\n"
            "/route What is machine learning?\n"
            "/route Translate: Buenos días\n"
            "/route Summarize: AI is transforming industries..."
        )
        return

    await message.bot.send_chat_action(message.chat.id, "typing")
    response = route_request(user_text)
    await message.answer(response)


@router.message(Command("sentiment"))
async def handle_sentiment(message: Message):
    """Handle /sentiment command - analyze text sentiment."""
    user_text = message.text.replace("/sentiment", "").strip()

    if not user_text:
        await message.answer(
            "Write text after /sentiment command.\n"
            "Example: /sentiment I love programming, it makes me happy!"
        )
        return

    await message.bot.send_chat_action(message.chat.id, "typing")
    response = analyze_sentiment(user_text)
    await message.answer(response, parse_mode="HTML")


@router.message(Command("tasks"))
async def handle_tasks(message: Message):
    """Handle /tasks command - extract tasks from text."""
    user_text = message.text.replace("/tasks", "").strip()

    if not user_text:
        await message.answer(
            "Write text after /tasks command.\n"
            "Example: /tasks Need to buy milk tomorrow, call John by Friday, finish report urgently"
        )
        return

    await message.bot.send_chat_action(message.chat.id, "typing")
    response = extract_tasks(user_text)
    await message.answer(response, parse_mode="HTML")


@router.message(Command("test"))
async def handle_test(message: Message):
    """Handle /test command - run prompt quality tests."""
    await message.answer("🧪 Running prompt tests... This may take a moment.")
    await message.bot.send_chat_action(message.chat.id, "typing")
    response = run_prompt_tests()
    await message.answer(response, parse_mode="HTML")


@router.message(Command("benchmark"))
async def handle_benchmark(message: Message):
    """Handle /benchmark command - benchmark Haiku vs Sonnet speed."""
    await message.answer("⏱ Running benchmarks... This may take up to 30 seconds.")
    await message.bot.send_chat_action(message.chat.id, "typing")
    response = run_benchmarks()
    await message.answer(response, parse_mode="HTML")


@router.message(Command("memory"))
async def handle_memory(message: Message):
    """Handle /memory command - show saved facts about user."""
    user_id = message.from_user.id
    facts = get_facts(user_id)

    if not facts:
        await message.answer("No facts saved about you yet. Just chat with me!")
        return

    facts_text = "\n".join(f"- {fact}" for fact in facts)
    await message.answer(f"🧠 <b>What I know about you:</b>\n\n{facts_text}", parse_mode="HTML")


@router.message(Command("forget"))
async def handle_forget(message: Message):
    """Handle /forget command - clear all saved facts about user."""
    user_id = message.from_user.id
    clear_facts(user_id)
    await message.answer("🗑 All facts about you have been cleared.")


@router.message(Command("summarize_note"))
async def handle_summarize_note(message: Message):
    """Handle /summarize_note command - summarize note using MCP sampling."""
    user_text = message.text.replace("/summarize_note", "").strip()

    if not user_text:
        await message.answer(
            "Write note title after /summarize_note command.\n"
            "Example: /summarize_note Shopping"
        )
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    response = await run_mcp_agent(f"summarize note '{user_text}' using tool_summarize_note_with_sampling")
    await message.answer(response)


@router.message(Command("process_notes"))
async def handle_process_notes(message: Message):
    """Handle /process_notes command - process all notes with progress notifications."""
    await message.answer("⚙️ Processing notes...")
    await message.bot.send_chat_action(message.chat.id, "typing")

    response = await run_mcp_agent("process all notes using tool_process_notes_with_progress")
    await message.answer(response)


@router.message(Command("roots"))
async def handle_roots(message: Message):
    """Handle /roots command - show accessible roots via MCP."""
    await message.bot.send_chat_action(message.chat.id, "typing")
    response = await run_mcp_agent("list all roots using tool_list_roots")
    await message.answer(response)


@router.message(Command("mcp_http"))
async def handle_mcp_http(message: Message):
    """Handle /mcp_http command - uses HTTP transport MCP server."""
    user_text = message.text.replace("/mcp_http", "").strip()

    if not user_text:
        await message.answer(
            "Write a request after /mcp_http command.\n"
            "Example: /mcp_http show all notes\n\n"
            "Note: HTTP MCP server must be running on port 8000."
        )
        return

    await message.bot.send_chat_action(message.chat.id, "typing")
    response = await run_mcp_http_agent(user_text)
    await message.answer(response)


@router.message(F.text)
async def handle_message(message: Message):
    """Handle regular text messages with long-term memory support."""
    user_id = message.from_user.id
    user_text = message.text

    # Extract and save facts from user message in background
    extract_and_save_facts(user_id, user_text)

    # Add user message to conversation history
    conversation_manager.add_message(user_id, "user", user_text)
    history = conversation_manager.get_history(user_id)

    await message.bot.send_chat_action(message.chat.id, "typing")

    # Ask Claude with long-term memory injected
    response = ask_claude_with_memory(
        user_id=user_id,
        messages=history,
        base_system=SYSTEM_PROMPT
    )

    conversation_manager.add_message(user_id, "assistant", response)
    await message.answer(response)