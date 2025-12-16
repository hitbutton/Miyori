import sys
import os

# Add project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.implementations.llm.google_ai_backend import GoogleAIBackend

def test_llm():
    print("Initializing GoogleAIBackend...")
    try:
        backend = GoogleAIBackend()
    except Exception as e:
        print(f"Failed to initialize backend: {e}")
        return

    prompt = "Hello! Please reply with 'Test successful'."
    print(f"\nSending prompt: '{prompt}'")
    print("-" * 20)
    
    def on_chunk(text):
        print(text, end="", flush=True)

    try:
        backend.generate_stream(prompt, on_chunk)
        print("\n" + "-" * 20)
        print("LLM Test Completed.")
    except Exception as e:
        print(f"\nError during generation: {e}")

if __name__ == "__main__":
    test_llm()
