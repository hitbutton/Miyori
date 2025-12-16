import google.generativeai as genai
import json
from pathlib import Path
from typing import Callable
from src.interfaces.llm_backend import ILLMBackend

class GoogleAIBackend(ILLMBackend):
    def __init__(self):
        # e:/_Projects/Miyori/src/implementations/llm/google_ai_backend.py
        # parent -> llm
        # parent.parent -> implementations
        # parent.parent.parent -> src
        # parent.parent.parent.parent -> Miyori
        config_path = Path(__file__).parent.parent.parent.parent / "config.json"
        
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        llm_config = config.get("llm", {})
        api_key = llm_config.get("api_key")
        model_name = llm_config.get("model", "gemini-2.0-flash-exp")
        
        if api_key:
            genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(model_name)

    def generate_stream(self, prompt: str, on_chunk: Callable[[str], None]) -> None:
        print("Thinking...")
        response = self.model.stream_generate_content(prompt)
        for chunk in response:
            if chunk.text:
                on_chunk(chunk.text)
