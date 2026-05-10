import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_PASSWORD = os.getenv("BOT_PASSWORD", "mypassword")

# Claude settings
CLAUDE_HAIKU = "claude-haiku-4-5-20251001"  # Default cheap and fast model
CLAUDE_SONNET = "claude-sonnet-4-6"  # For complex tasks
MAX_TOKENS = 1024  # Max tokens per response
TEMPERATURE = 1  # 1 - standard for Claude
MAX_HISTORY = 20  # Max messages in conversation history
MULTILINGUAL_INSTRUCTION = ("Always respond in the same language as the note or user's message content. "
                            "If the content is in Russian, respond in Russian.")