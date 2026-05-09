from bot.config import MAX_HISTORY


class ConversationManager:
    """
    Manages conversation history for each user.
    Key - telegram user_id, value - list of messages.
    """
    def __init__(self):
        self.histories: dict[int, list] = {}

    def add_message(self, user_id: int, role: str, content: str):
        """Add a message to the user's history."""
        if user_id not in self.histories:
            self.histories[user_id] = []

        self.histories[user_id].append({
            "role": role,
            "content": content
        })

        # Trim history if it exceeds the limit
        if len(self.histories[user_id]) > MAX_HISTORY:
            self.histories[user_id] = self.histories[user_id][-MAX_HISTORY:]

    def get_history(self, user_id: int) -> list:
        """Get the user's conversation history."""
        return self.histories.get(user_id, [])

    def clear_history(self, user_id: int):
        """Clear the user's conversation history."""
        self.histories[user_id] = []