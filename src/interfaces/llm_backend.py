"""LLM Backend Interface

This interface defines the contract for Large Language Model implementations.
Any class implementing this interface must provide a generate_stream() method
that takes a prompt and a callback, streaming AI-generated response chunks.
"""

from abc import ABC, abstractmethod
from typing import Callable


class ILLMBackend(ABC):
    """Interface for LLM backend implementations"""
    
    @abstractmethod
    def generate_stream(self, prompt: str, on_chunk: Callable[[str], None]) -> None:
        """Generate an AI response with streaming chunks.
        
        Args:
            prompt: The user's input text to generate a response for
            on_chunk: Callback function called with each text chunk as it arrives
        """
        pass

    @abstractmethod
    def reset_context(self) -> None:
        """Reset the conversation context (history)."""
        pass
