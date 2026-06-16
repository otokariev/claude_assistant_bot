from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Create main keyboard with all bot commands."""
    buttons = [
        [KeyboardButton(text="/help"), KeyboardButton(text="/clear")],
        [KeyboardButton(text="/recall"), KeyboardButton(text="/new_project")],
        [KeyboardButton(text="/switch_project"), KeyboardButton(text="/projects")],
        [KeyboardButton(text="/export_history"), KeyboardButton(text="/delete_project")],
        [KeyboardButton(text="/forget"), KeyboardButton(text="/mcp")],
        [KeyboardButton(text="/upload"), KeyboardButton(text="/ask_with_rag")],
        [KeyboardButton(text="/chain"), KeyboardButton(text="/parallel")],
        [KeyboardButton(text="/route"), KeyboardButton(text="/stream")],
        [KeyboardButton(text="/sentiment"), KeyboardButton(text="/tasks")],
        [KeyboardButton(text="/summarize_note"), KeyboardButton(text="/process_notes")],
        [KeyboardButton(text="/roots"), KeyboardButton(text="/mcp_http")],
        [KeyboardButton(text="/test"), KeyboardButton(text="/benchmark")],
        [KeyboardButton(text="/memory"), KeyboardButton(text="/note")],
    ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Choose a command or type a message..."
    )