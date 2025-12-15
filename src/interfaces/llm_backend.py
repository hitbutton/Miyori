"""LLM Backend Interface

This interface defines the contract for Large Language Model implementations.
Any class implementing this interface must provide a generate() method
that takes a prompt and returns an AI-generated response.
"""

from abc import ABC, abstractmethod


class ILLMBackend(ABC):
    """Interface for LLM backend implementations"""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate an AI response to the given prompt.
        
        Args:
            prompt: The user's input text to generate a response for
            
        Returns:
            str: The AI-generated response text
        """
        pass
