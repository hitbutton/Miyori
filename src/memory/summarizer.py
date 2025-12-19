from google import genai
import json
from pathlib import Path

class Summarizer:
    def __init__(self, client: genai.Client = None):
        self.client = client
        if not self.client:
            # Load config to initialize client if not provided
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.json"
            with open(config_path, 'r') as f:
                config = json.load(f)
            llm_config = config.get("llm", {})
            api_key = llm_config.get("api_key")
            if api_key:
                self.client = genai.Client(api_key=api_key)
            else:
                print("Warning: API Key not found for Summarizer")
        
        # Use a cheap/fast model for summarization
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.model_name = config.get("llm", {}).get("model", "gemini-1.5-flash-8b") # Use 8b if possible for speed/cost

    async def create_summary(self, user_msg: str, assistant_msg: str) -> str:
        """Create a semantic summary of the exchange using the LLM."""
        if not self.client:
            # Fallback to simple concatenation if LLM unavailable
            return f"User: {user_msg[:100]} | Assistant: {assistant_msg[:100]}"

        prompt = f"""Summarize this conversation exchange in 2-3 sentences.
Preserve: key facts, emotions, decisions, and context.

User: {user_msg}
Assistant: {assistant_msg}

Summary:"""

        try:
            # Running the sync client call in a thread to keep it async-friendly
            import asyncio
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, lambda: self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            ))
            return response.text.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Turn summary: {user_msg[:50]}..."
