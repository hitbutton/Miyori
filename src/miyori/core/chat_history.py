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
        return self._calculate_tokens(self.messages)

    def _calculate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """Calculates token count for a list of messages."""
        total_tokens = 0
        for msg in messages:
            content = msg.get("content", "")
            total_tokens += len(str(content)) // 4
            
            if "tool_calls" in msg:
                for tool_call in msg["tool_calls"]:
                    total_tokens += len(str(tool_call)) // 4
                    
            for key, value in msg.items():
                if key not in ["role", "content", "tool_calls"]:
                    total_tokens += len(str(value)) // 4
        return total_tokens

    def clear(self) -> None:
        """Resets the history."""
        self.messages = []

    def trim_to_limit(self, max_tokens: int, chunk_size: int) -> None:
        """
        Turn-aware trimming: remove oldest turns until token count is under limit.
        Always starts history with a 'user' message.
        """
        current_tokens = self.get_token_count()
        if current_tokens <= max_tokens:
            return

        print(f"ChatHistory: Trimming history. Current tokens: {current_tokens}, Limit: {max_tokens}")
        
        target_tokens = max_tokens - chunk_size
        
        # Identify all indices of 'user' messages (safe starting points)
        user_indices = [i for i, msg in enumerate(self.messages) if msg["role"] == "user"]
        
        if not user_indices:
            # Fallback if no user messages exist (shouldn't happen in normal flow)
            while self.messages and self.get_token_count() > target_tokens:
                if len(self.messages) <= 1: break
                self.messages.pop(0)
            print(f"ChatHistory: Trimming complete (fallback). New tokens: {self.get_token_count()}")
            return

        # We want to find the first user turn that brings us under the limit.
        # We MUST keep at least the last user turn.
        new_start_index = user_indices[-1] # Default to keeping only the last turn
        
        for idx in user_indices:
            # If keeping messages from this idx onwards fits in target_tokens
            if self._calculate_tokens(self.messages[idx:]) <= target_tokens:
                new_start_index = idx
                break
            # If we are at the last user index and even it doesn't fit, 
            # we've already set new_start_index = user_indices[-1].
            
        if new_start_index > 0:
            self.messages = self.messages[new_start_index:]
            
        print(f"ChatHistory: Trimming complete. New tokens: {self.get_token_count()}")
