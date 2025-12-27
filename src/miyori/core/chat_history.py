from typing import List, Dict, Any, Optional

class ChatHistory:
    """
    Manages conversation message history with token limits and greedy trimming.
    Internal Format:
    - {"role": "user", "content": "..."}
    - {"role": "miyori", "content": "...", "tool_calls": [...]}
    - {"role": "tool", "content": "...", "name": "tool_name", "tool_call_id": "..."}
    """

    def __init__(self, max_tokens: int = 8000, trim_chunk_size: int = 1000):
        self.messages: List[Dict[str, Any]] = []
        self.max_tokens = max_tokens
        self.trim_chunk_size = trim_chunk_size

    def add_message(self, role: str, content: str, **kwargs) -> None:
        """
        Adds a message to the history and trims if necessary.
        """
        message = {"role": role, "content": content}
        message.update(kwargs)
        self.messages.append(message)
        
        # Trim if we exceed the limit
        self.trim_to_limit(self.max_tokens, self.trim_chunk_size)

    def get_history(self) -> List[Dict[str, Any]]:
        """Returns the current message history."""
        return self.messages

    def get_token_count(self) -> int:
        """
        Simple character-based heuristic: len(content) // 4.
        Applies to all content in the messages.
        """
        total_tokens = 0
        for msg in self.messages:
            content = msg.get("content", "")
            total_tokens += len(str(content)) // 4
            
            # Count tokens for tool calls if present
            if "tool_calls" in msg:
                for tool_call in msg["tool_calls"]:
                    total_tokens += len(str(tool_call)) // 4
                    
            # Count tokens for other fields if present (name, tool_call_id)
            for key, value in msg.items():
                if key not in ["role", "content", "tool_calls"]:
                    total_tokens += len(str(value)) // 4
                    
        return total_tokens

    def clear(self) -> None:
        """Resets the history."""
        self.messages = []

    def trim_to_limit(self, max_tokens: int, chunk_size: int) -> None:
        """
        Greedy trimming: remove oldest messages until token count is comfortably under limit.
        """
        current_tokens = self.get_token_count()
        if current_tokens <= max_tokens:
            return

        print(f"ChatHistory: Trimming history. Current tokens: {current_tokens}, Limit: {max_tokens}")
        
        # Algorithm: Remove oldest messages until current_tokens < max_tokens - chunk_size
        target_tokens = max_tokens - chunk_size
        
        while self.messages and self.get_token_count() > target_tokens:
            # We must be careful not to remove the last message if it's the one we just added?
            # Actually, trim_to_limit is called after add_message.
            # Usually we don't want to remove the message that was JUST added unless it's huge.
            if len(self.messages) <= 1:
                break
            self.messages.pop(0)
            
        print(f"ChatHistory: Trimming complete. New tokens: {self.get_token_count()}")
