from google import genai
import json
from pathlib import Path
from typing import List

class EmbeddingService:
    def __init__(self):
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config.json"
        
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        llm_config = config.get("llm", {})
        memory_config = config.get("memory", {})
        
        self.api_key = llm_config.get("api_key")
        self.model_name = memory_config.get("embedding_model", "text-embedding-004")
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            print("Warning: API Key not found for EmbeddingService")

    def embed(self, text: str) -> List[float]:
        """Generate an embedding for the given text."""
        if not self.client:
            # MVP Fallback: return dummy zeros 
            return [0.0] * 768
            
        try:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 768
