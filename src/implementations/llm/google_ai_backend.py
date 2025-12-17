from google import genai
import json
from pathlib import Path
from typing import Callable
from src.interfaces.llm_backend import ILLMBackend

class GoogleAIBackend(ILLMBackend):
    def __init__(self):
        # e:/_Projects/Miyori/src/implementations/llm/google_ai_backend.py
        config_path = Path(__file__).parent.parent.parent.parent / "config.json"
        
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        llm_config = config.get("llm", {})
        self.api_key = llm_config.get("api_key")
        self.model_name = llm_config.get("model", "gemini-2.0-flash-exp")
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            # Handle missing API key gracefully or let it fail later
            # Handle missing API key gracefully or let it fail later
            self.client = None
            
        self.chat = None

    def reset_context(self) -> None:
        """Resets the conversation history."""
        print("Resetting conversation context...")
        self.chat = None

    def generate_stream(self, prompt: str, on_chunk: Callable[[str], None]) -> None:
        if not self.client:
            print("Error: API Key not configured.")
            return

        print("Thinking...")
        
        # Initialize chat if not already active
        if self.chat is None:
            # We can create a new chat session
            try:
                self.chat = self.client.chats.create(model=self.model_name)
            except Exception as e:
                print(f"Error creating chat session: {e}")
                # Fallback to direct generation if chat fails (though unexpected)
                # But better to just re-raise or handle gracefully
                return

        try:
            # Use chat.send_message with streaming
            response = self.chat.send_message_stream(prompt)
            
            for chunk in response:
                if chunk.text:
                    on_chunk(chunk.text)
                    
        except Exception as e:
            print(f"Error during streaming generation: {e}")
            self.chat = None # Invalidate chat on error?
