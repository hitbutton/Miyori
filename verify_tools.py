import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.implementations.llm.google_ai_backend import GoogleAIBackend
from src.core.tool_registry import ToolRegistry
from src.tools.web_search import web_search_tool
from src.tools.file_ops import file_ops_tool
from typing import Dict, Any

def test_tools():
    print("🚀 Starting Tool Calling Verification...")
    
    # Setup tools
    registry = ToolRegistry()
    registry.register(web_search_tool)
    registry.register(file_ops_tool)
    
    backend = GoogleAIBackend()
    
    def on_chunk(text: str):
        print(f"AI: {text}", end="", flush=True)
        
    def on_tool_call(name: str, args: Dict[str, Any]) -> str:
        print(f"\n🔧 Executing tool: {name} with args: {args}")
        result = registry.execute(name, **args)
        return result

    # Test Case 1: Web Search
    print("\n--- Test 1: Web Search ---")
    prompt1 = "What is the capital of France and what is the current time there? Use search."
    backend.generate_stream_with_tools(prompt1, registry.get_all(), on_chunk, on_tool_call)
    print("\nTest 1 Complete.")

    # Test Case 2: File Operations
    print("\n--- Test 2: File Operations (List) ---")
    prompt2 = "List the files in the workspace directory."
    backend.generate_stream_with_tools(prompt2, registry.get_all(), on_chunk, on_tool_call)
    print("\nTest 2 Complete.")

    # Test Case 3: File Operations (Write)
    print("\n--- Test 3: File Operations (Write) ---")
    prompt3 = "Write 'Hello from Miyori' to a file named 'test.txt' in the workspace directory."
    backend.generate_stream_with_tools(prompt3, registry.get_all(), on_chunk, on_tool_call)
    print("\nTest 3 Complete.")

if __name__ == "__main__":
    test_tools()
