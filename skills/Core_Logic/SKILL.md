# Skill: Core Agentic Logic & Control Flow

This skill covers the primary orchestration logic of Miyori, including how user inputs are processed, how the agentic loop is managed, and the relationship between the Core and the LLM Coordinator.

## Key Components

### 1. MiyoriCore (`src/miyori/core/miyori.py`)
The central entry point for all interactions.
- `process_input(text, source, on_chunk)`: 
    - Handles "wake-word" logic for voice.
    - Routes input to `_handle_with_tools` if a tool registry is present.
- `_handle_with_tools(user_input, source, on_chunk)`:
    - Sets up the `on_tool_call` execution handler.
    - Passes registered tools to the LLM backend.

### 2. AgenticState (`src/miyori/core/agentic_state.py`)
Tracks the state of a multi-step task.
- `max_iterations`: Set to **50** (Updated from 25).
- `iteration`: Current step count.
- `objective`: The current goal being pursued.
- `is_active`: Boolean flag indicating if an agentic loop is running.

### 3. LLMCoordinator (`src/miyori/core/llm_coordinator.py`)
Manages the actual conversation loop with the LLM provider.
- `run(...)`:
    - Injects memory context and agentic state into the prompt.
    - Manages the `while True` loop for tool calling.
    - Checks for interrupts and iteration limits.
    - Strips internal metadata (like thought signatures) before storing history.

## Control Flow
1. **Input Arrival**: `MiyoriCore.process_input` is called.
2. **LLM Request**: `GoogleAIBackend.llm_chat` calls `LLMCoordinator.run`.
3. **Looping**: `LLMCoordinator` repeatedly calls the provider API.
4. **Tool Execution**: If the LLM requests a tool, `on_tool_call` in `MiyoriCore` executes it via `ToolRegistry`.
5. **Memory Context**: Every turn, `LLMCoordinator` uses the `context_builder` (Memory Retrieval) to find relevant past interactions.

## Security & Safety
- **Terminal Approval**: All shell commands via `terminal` tool require manual console approval (`y/n`).
- **Interrupts**: The `StateManager` can flag an interrupt to stop long-running generations.
