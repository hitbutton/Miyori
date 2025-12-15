"""Speech Input Interface

This interface defines the contract for speech input implementations.
Any class implementing this interface must provide a listen() method
that captures audio and returns transcribed text.
"""

from abc import ABC, abstractmethod


class ISpeechInput(ABC):
    """Interface for speech input implementations"""
    
    @abstractmethod
    def listen(self) -> str | None:
        """Listen to audio input and return transcribed text.
        
        Returns:
            str: The transcribed text from speech
            None: If speech recognition failed or no speech detected
        """
        pass
