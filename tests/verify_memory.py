import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.implementations.llm.google_ai_backend import GoogleAIBackend

async def verify_memory():
    print("--- Memory Verification Test ---")
    backend = GoogleAIBackend()
    
    # 1. Test Context Retrieval (Empty)
    print("\nTesting context retrieval on first message...")
    def dummy_callback(chunk): pass
    backend.generate_stream("Hello, I'm Simon. I'm a software engineer.", dummy_callback)
    
    # Wait for async storage
    print("Waiting for async storage and embedding...")
    await asyncio.sleep(5)
    
    # 2. Verify storage
    episodes = backend.store.search_episodes([0.0]*768, limit=10, status='active')
    if episodes:
        print(f"SUCCESS: Stored episode found: '{episodes[0]['summary']}'")
    else:
        # Check pending
        pending = backend.store.search_episodes([0.0]*768, limit=10, status='pending_embedding')
        if pending:
            print(f"INFO: Episode is still pending: '{pending[0]['summary']}'")
        else:
            print("FAILURE: No episode stored.")

    # 3. Test Context Injection
    print("\nTesting context injection on second message...")
    backend.reset_context()
    backend.generate_stream("What do you know about me?", dummy_callback)
    
    # 4. Cleanup
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(verify_memory())
