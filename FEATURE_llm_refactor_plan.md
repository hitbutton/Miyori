# LLM Backend Refactoring Implementation Plan

## Overview
Separate provider-agnostic orchestration logic from Google AI-specific implementation, replacing Google's chat session management with our own history tracking.

**IMPORTANT:** This refactoring does NOT touch the existing memory systems (SQLiteMemoryStore, EpisodicMemoryManager, ConsolidationManager, etc.). Those remain intact. We're only replacing Google's `chat_session` with our own runtime message history.

## Message Format Convention

**Internal Format (throughout codebase):**
```python
{"role": "user", "content": "..."}
{"role": "miyori", "content": "...", "tool_calls": [...]}  # AI responses
{"role": "tool", "content": "...", "name": "tool_name", "tool_call_id": "..."}
```

**Why "miyori" instead of "assistant":**
- Aligns with project vision and AI identity
- No "assistant" framing anywhere in internal code, logs, or history
- Provider-specific translations handle mapping to/from provider formats:
  - Google: `"miyori"` ↔ `"model"`
  - OpenAI (future): `"miyori"` ↔ `"assistant"`
  - Local models (future): `"miyori"` ↔ whatever they expect

**Multiple Tool Calls Per Turn:**
A single miyori response can contain multiple tool calls. The internal format supports this:
```python
{
    "role": "miyori",
    "content": "I'll check both of those for you.",
    "tool_calls": [
        {"id": "call_1", "name": "get_weather", "arguments": {...}},
        {"id": "call_2", "name": "get_calendar", "arguments": {...}}
    ]
}
```

Each tool call gets its own tool result message:
```python
{"role": "tool", "content": "Result 1", "name": "get_weather", "tool_call_id": "call_1"}
{"role": "tool", "content": "Result 2", "name": "get_calendar", "tool_call_id": "call_2"}
```

**Token Counting:**
- Simple character-based heuristic: `len(content) // 4`
- Applies to all message content including tool outputs
- Approximation is acceptable for history management

**Caching Optimization:**
- Memory context prefixed to user message (not in system instruction)
  - Format: `"[CONTEXT: date/time, relevant memories]\n\n{user_prompt}"`
  - Keeps base system instruction stable for provider-side caching
  - Memory context varies per turn, so goes in user message
- History trimming done greedily in large chunks
  - Better to remove more than not enough
  - Maximizes cache hit rates by maintaining stable history prefixes

## New Generic Components

### 1. `miyori/core/chat_history.py`
**Purpose:** Manage conversation message history with token limits

**Responsibilities:**
- Store messages in internal format
- Simple token counting (character-based heuristic: `len(content) // 4`)
- Count tokens for all message types including tool outputs
- Greedy trimming: remove oldest messages until well under limit
- Provide current history for API calls
- Clear/reset history

**Interface:**
```python
class ChatHistory:
    def add_message(role: str, content: str, **kwargs) -> None
    def get_history() -> List[Dict]
    def get_token_count() -> int
    def clear() -> None
    def trim_to_limit(max_tokens: int, chunk_size: int) -> None
```

**Trimming Strategy (Greedy Removal):**
- When token limit exceeded, remove oldest messages in chunks
- Keep removing until token count is comfortably under limit
- Algorithm: Remove `chunk_size` tokens worth of oldest messages at a time
- Continue removing until `current_tokens < max_tokens - chunk_size` (leave buffer)
- Maximizes provider-side cache hits by keeping stable history prefixes

### 2. `miyori/core/llm_coordinator.py`
**Purpose:** Provider-agnostic orchestration of LLM conversations

**Responsibilities:**
- Manage conversation flow with tool calling loop
- Coordinate streaming via callbacks
- Handle interrupt checking
- Enforce max turns limit
- Inject passive memory context as prefix to user messages
- Integrate with chat history
- Trigger memory storage after turns
- Handle multiple tool calls per turn

**Dependencies (injected):**
- ChatHistory instance
- Provider-specific callbacks (see below)
- Memory context builder (optional, for retrieving passive memories)
- Configuration limits from provider (max_tokens, max_turns, trim_chunk_size)

**Workflow:**
1. Accept user prompt
2. Get current datetime string
3. Retrieve memory context (if enabled) via `context_builder.build_context(prompt)`
4. Build contextualized prompt:
   ```
   [CONTEXT: {datetime}, {memory_summary}]
   
   {user_prompt}
   ```
5. Get message history from ChatHistory
6. Append contextualized user message to history
7. Trim history if over token limit (greedy removal)
8. Translate history to provider format via callback
9. Call provider's API via `_call_provider_api` callback
10. Parse response via `_parse_provider_response` callback
11. Stream text chunks via `on_chunk`
12. If tool calls detected (can be multiple):
    - For each tool call:
      - Execute via `on_tool_call`
      - Format result via `_format_tool_result` callback
      - Add to ChatHistory as tool message with tool_call_id
    - Continue loop with all tool results (up to max_turns)
13. Add final miyori response to ChatHistory (with tool_calls if present)
14. Trigger memory storage via `_store_turn` callback (if enabled)

**Multiple Tool Calls Handling:**
- A single API response may contain multiple tool calls
- All tool calls are executed in sequence
- All tool results are sent back to the API in the next turn
- Each tool result is stored as a separate message in history with proper tool_call_id

## Modified Google AI Backend

### `implementations/llm/google_ai_backend.py`

**What Stays:**
- All memory system initialization and components
- System instruction file loading (base system instruction only)
- Configuration loading
- Logging functionality (`_send_to_log`)
- Memory storage (`_store_turn`) 
- Memory cleanup (`_cleanup_async_memory`)
- Tool format conversion (`_convert_tools_to_gemini_format`)
- Memory context retrieval via `context_builder.build_context()` (but used differently)

**What Changes:**
- **Remove** `self.chat_session` management entirely
- **Switch** to stateless `client.models.generate_content()` API
- Instantiate `ChatHistory` and `LLMCoordinator`
- Implement provider-specific callbacks for coordinator
- Define provider-specific limits (hardcoded constants):
  - `MAX_HISTORY_TOKENS = 8000` (or appropriate for model)
  - `MAX_TOOL_TURNS = 5`
  - `TRIM_CHUNK_SIZE = 1000` (tokens to remove at once when trimming)
- Memory context handling changes:
  - No longer used in system instruction
  - Coordinator receives memory context and prefixes to user message
  - System instruction stays stable (only base instructions from file)
- `llm_chat()` becomes simple delegation to coordinator
- `reset_context()` now clears ChatHistory instead of chat_session

**New Methods (Provider-Specific Callbacks):**

#### 1. `_translate_to_provider_format(messages: List[Dict]) -> List[Content]`
Converts internal format to Google's Content/Parts format.

**Handles:**
- Role mapping: `"miyori"` → `"model"`, `"user"` → `"user"`
- Multiple tool calls in a single miyori message
- Tool result messages (with tool_call_id matching)
- Text content and function calls as Parts

**Returns:** List of `types.Content` objects ready for Google API

**Example Internal → Google Mapping:**
```python
# Internal:
{"role": "miyori", "content": "Let me check that", "tool_calls": [
    {"id": "1", "name": "search", "arguments": {"query": "..."}}
]}

# Google:
Content(
    role="model",
    parts=[
        Part(text="Let me check that"),
        Part(function_call=FunctionCall(name="search", args={...}))
    ]
)
```

#### 2. `_call_provider_api(provider_messages: List[Content], config: GenerateContentConfig) -> GenerateContentResponse`
Makes stateless API call to Google's generate_content.

**Uses:** `client.models.generate_content(model=model_name, contents=provider_messages, config=config)`

**Not** using chat sessions anymore - this is a stateless call with full history.

**Returns:** Raw Google API response

#### 3. `_parse_provider_response(response: GenerateContentResponse) -> Dict`
Extracts text and tool calls from Google response.

**Handles:**
- Multiple parts in response (text + multiple function calls)
- Generates unique tool_call_ids for tracking
- Extracts function call names and arguments

**Returns:**
```python
{
    "text": str,  # Combined text from all text parts
    "tool_calls": [  # May be empty, may have multiple
        {
            "id": "call_xyz",  # Generated ID for tracking
            "name": "function_name",
            "arguments": {...}
        }
    ]
}
```

#### 4. `_format_tool_result(tool_call_id: str, tool_name: str, result: str) -> Content`
Converts tool result to Google's Content format for submission.

**Returns:** `Content` object with function_response Part that Google expects

**Modified `llm_chat()` Structure:**
```python
def llm_chat(prompt, tools, on_chunk, on_tool_call, interrupt_check):
    self.coordinator.run(
        prompt=prompt,
        tools=tools,
        on_chunk=on_chunk,
        on_tool_call=on_tool_call,
        interrupt_check=interrupt_check,
        context_builder=self.context_builder,
        store_turn_callback=self._store_turn
    )
```

**Memory Context Handling:**
- Coordinator calls `context_builder.build_context(prompt)` to get passive memories
- Coordinator gets current datetime
- Formats as: `"[CONTEXT: {datetime}, {memories}]\n\n{user_prompt}"`
- This keeps base system instruction stable for caching

## Implementation Steps

### Phase 1: Create Generic Components
1. **Implement `chat_history.py`**
   - Message storage with internal format (user/miyori/tool roles)
   - Support for tool_calls array in miyori messages
   - Support for tool_call_id in tool messages
   - Token counting heuristic (applies to all message content)
   - Greedy history trimming logic
   - Unit tests

2. **Implement `llm_coordinator.py`**
   - Core orchestration flow
   - Memory context retrieval and prefixing to user message
   - Datetime injection in context prefix
   - Tool calling loop with multiple tool call support
   - Interrupt handling
   - Greedy history trimming integration
   - Callback interface for provider-specific operations
   - Unit tests with mock callbacks

### Phase 2: Refactor Google Backend
1. **Add callback methods to `GoogleAIBackend`:**
   - `_translate_to_provider_format` (handles multiple tool calls per turn)
   - `_call_provider_api` (uses stateless generate_content, not chat session)
   - `_parse_provider_response` (extracts multiple tool calls if present)
   - `_format_tool_result` (formats for Google's function_response)

2. **Modify `__init__`:**
   - Define provider-specific constants:
     - `MAX_HISTORY_TOKENS = 8000` (or appropriate for model)
     - `MAX_TOOL_TURNS = 5`
     - `TRIM_CHUNK_SIZE = 1000` (tokens to remove at once when over limit)
   - Instantiate `ChatHistory` with max_history_tokens limit
   - Instantiate `LLMCoordinator` with callbacks, limits, and context_builder
   - Remove `chat_session` initialization

3. **Simplify `llm_chat()`:**
   - Delegate to coordinator with context_builder and store_turn callback
   - Remove manual memory context building (coordinator handles it)
   - Remove system instruction assembly (stays static from file)
   - Keep logging integration

4. **Update `reset_context()`:**
   - Clear ChatHistory instead of chat_session
   - Clear async memory stream context (already present)

### Phase 3: Testing & Validation
1. Test with existing tools
2. Test multiple tool calls in single turn
3. Verify memory integration still works
4. Verify memory context appears as prefix in user messages
5. Verify datetime appears in context prefix
6. Verify interrupt functionality
7. Verify streaming behavior
8. Test token limit trimming:
   - Verify greedy removal (removes enough to create buffer)
   - Verify trim chunk size is respected
9. Test max turns limiting
10. Verify role mapping (miyori ↔ model) works correctly
11. Check that "miyori" appears in logs, not "assistant" or "model"
12. Verify system instruction stays stable (base only, no memory appended)
13. Verify stateless API calls work correctly (no chat_session dependency)

## Preserved Functionality Checklist

- ✓ System instruction loading from file (remains stable, no memory appended)
- ✓ Memory retrieval and context building (now prefixed to user message)
- ✓ Datetime context injection (new: added to context prefix)
- ✓ Episodic memory storage after turns
- ✓ Memory gating (if enabled)
- ✓ Async memory streaming and prefetching
- ✓ Tool calling with result feedback (enhanced: multiple calls per turn)
- ✓ Streaming response chunks
- ✓ Interrupt checking during generation
- ✓ Max turns limiting
- ✓ Conversation reset
- ✓ Logging to files
- ✓ Error handling throughout
- ✓ Background async loop for memory tasks
- ✓ Phase 3 memory components (consolidation, semantic extraction)

## Benefits of This Architecture

1. **Reusability:** New providers (OpenAI, Anthropic, local models) only need to implement 4 callback methods
2. **Testability:** Generic components can be unit tested independently
3. **Maintainability:** Orchestration logic in one place, not duplicated per provider
4. **Control:** We manage history and token limits, not provider-specific sessions
5. **Flexibility:** Easy to swap providers or run A/B tests
6. **Cache Efficiency:**
   - Stable system instructions maximize provider-side caching
   - Memory context in user message (not system instruction) keeps prompts cacheable
   - Greedy history trimming maintains stable prefixes for better cache hits
7. **Multiple Tool Calls:** Proper support for multiple tool invocations per turn