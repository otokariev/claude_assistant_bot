from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Create main keyboard with all bot commands."""
    buttons = [
        [KeyboardButton(text="/help"), KeyboardButton(text="/clear")],
        [KeyboardButton(text="/memory"), KeyboardButton(text="/forget")],
        [KeyboardButton(text="/note"), KeyboardButton(text="/mcp")],
        [KeyboardButton(text="/upload"), KeyboardButton(text="/ask_with_rag")],
        [KeyboardButton(text="/chain"), KeyboardButton(text="/parallel")],
        [KeyboardButton(text="/route"), KeyboardButton(text="/stream")],
        [KeyboardButton(text="/sentiment"), KeyboardButton(text="/tasks")],
        [KeyboardButton(text="/summarize_note"), KeyboardButton(text="/process_notes")],
        [KeyboardButton(text="/roots"), KeyboardButton(text="/mcp_http")],
        [KeyboardButton(text="/test"), KeyboardButton(text="/benchmark")],
    ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Choose a command or type a message..."
    )