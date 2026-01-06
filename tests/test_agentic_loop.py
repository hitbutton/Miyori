import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from miyori.core.agentic_state import AgenticState, AgenticExitSignal
from miyori.core.llm_coordinator import LLMCoordinator
from miyori.core.chat_history import ChatHistory
from miyori.tools.agentic_loop import create_agentic_loop_tool
from miyori.tools.exit_loop import exit_loop_tool
from miyori.tools.terminal import create_terminal_tool
from miyori.core.tool_registry import ToolRegistry

def test_agentic_loop_logic():
    print("Testing Agentic Loop Logic...")
    
    # 1. Setup State and Registry
    state = AgenticState()
    registry = ToolRegistry()
    registry.register(create_agentic_loop_tool(state))
    registry.register(exit_loop_tool)
    registry.register(create_terminal_tool(state))
    
    # 2. Test explicit exit signal
    print("\nTesting exit_loop tool signal...")
    try:
        registry.execute("exit_loop", result="Test success", status="success")
        print("[FAIL] exit_loop did not raise AgenticExitSignal")
    except AgenticExitSignal as e:
        print(f"[SUCCESS] Caught expected signal: {e}")
        assert e.result == "Test success"
        assert e.status == "success"

    # 3. Test agentic_loop tool state update
    print("\nTesting agentic_loop tool initialization...")
    registry.execute("agentic_loop", objective="Verify implementation", user_prompt="Initial prompt")
    assert state.is_active == True
    assert state.objective == "Verify implementation"
    assert state.original_prompt == "Initial prompt"
    assert state.iteration == 1
    print("[SUCCESS] Agentic state initialized correctly.")

    # 4. Test terminal tool persistence (CWD)
    print("\nTesting terminal tool CWD tracking...")
    initial_cwd = state.working_directory or ""
    registry.execute("terminal", command="cd ..", persistent=True)
    new_cwd = state.working_directory
    print(f"Old CWD: {initial_cwd}")
    print(f"New CWD: {new_cwd}")
    assert new_cwd != initial_cwd
    print("[SUCCESS] Terminal tool tracked CWD change.")

def test_coordinator_integration_mock():
    print("\nTesting Coordinator Integration (Mocked LLM)...")
    
    chat_history = ChatHistory(max_tokens=1000)
    
    # Mock callbacks
    def translate(h): return h
    def parse(r): return r
    def format(id, name, res): return res
    
    responses = [
        # Step 1: LLM calls agentic_loop
        {"text": "I will start an agentic loop.", "tool_calls": [{"id": "1", "name": "agentic_loop", "arguments": {"objective": "Mock Task"}}]},
        # Step 2: LLM performs an action
        {"text": "Step 1 complete.", "tool_calls": [{"id": "2", "name": "terminal", "arguments": {"command": "echo Hello"}}]},
        # Step 3: LLM finishes
        {"text": "All done.", "tool_calls": [{"id": "3", "name": "exit_loop", "arguments": {"result": "Finished mock task", "status": "success"}}]}
    ]
    
    resp_iter = iter(responses)
    def call_api(m, c): return next(resp_iter)
    
    coordinator = LLMCoordinator(chat_history, translate, call_api, parse, format)
    state = AgenticState()
    
    def on_chunk(c): print(f"Chunk: {c}")
    
    # Tool execution callback that bridges coordinator to registry
    registry = ToolRegistry()
    registry.register(create_agentic_loop_tool(state))
    registry.register(exit_loop_tool)
    registry.register(create_terminal_tool(state))
    
    def on_tool(name, args):
        return registry.execute(name, **args)

    coordinator.run(
        prompt="Start task", 
        tools=registry.get_all(), 
        on_chunk=on_chunk, 
        on_tool_call=on_tool, 
        agentic_state=state
    )
    
    assert state.is_active == False # Should be reset after exit_loop
    print("[SUCCESS] Coordinator handled agentic loop and exited cleanly via tool signal.")

if __name__ == "__main__":
    test_agentic_loop_logic()
    test_coordinator_integration_mock()
