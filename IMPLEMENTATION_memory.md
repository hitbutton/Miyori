# Implementation Plan - Human-Like Memory System

This plan outlines the staged rollout of the Human-Like Memory System, incorporating final architectural fixes for reliable async embeddings, semantic summarization, and prioritized token management.

## Phase 1: Foundation (Production-Ready MVP)
Goal: Establish a robust async storage backend and the context injection loop.

### 1.1 Interfaces and Structure [NEW]
- Create `src/interfaces/memory.py` defining `IMemoryStore`.
- Create `src/memory/` directory.

### 1.2 SQLite Storage (Production Schema) [NEW]
- **Enhanced Schema**:
  - `episodic_memory`: summary, full_text (JSON), timestamp, embedding (BLOB), importance, emotional_valence, topics, entities, connections, **status** (`pending_embedding` | `active` | `archived`).
  - `semantic_memory`: fact, confidence, first_observed, last_confirmed, version_history (JSON), derived_from (JSON), contradictions (JSON), status.
  - `relational_memory`: category, data (JSON), confidence, evidence_count, last_updated.
  - `emotional_thread`: current_state, recognized_from, should_acknowledge, thread_length, last_update.
- **Transaction Safety**: Multi-step updates (like version history) wrapped in SQLite transactions.

### 1.3 Async Embedding Queue [NEW]
- Implement `EmbeddingQueue` in `src/memory/episodic.py`.
- **Logic**: 
  - Store episode with `status='pending_embedding'` immediately.
  - Queue for background processing via `asyncio.Queue`.
  - Process embeddings with Gemini `text-embedding-004`; update DB to `status='active'` on success.
  - **Retrieval Filter**: Only search episodes where `status='active'`.

### 1.4 Prioritized Context Injection [NEW]
- Implement `build_context()` with a 1000-token budget and strict priority:
  1. **RELATIONAL** (Personality/Style) - [REQUIRED]
  2. **EMOTIONAL** (Current Thread) - [REQUIRED]
  3. **RECENT** (Last 7 days, High Importance) - [HIGH]
  4. **FACTS** (Semantic Knowledge) - [MEDIUM]
  5. **RELEVANT** (Semantic Retrieval Results) - [FILL]
- **Truncation**: Drop items at boundaries (complete memories), never mid-sentence. Drop least relevant/oldest first.

### 1.5 LLM Summarization Strategy [NEW]
- Implement `create_summary()` using Gemini Flash.
- **Scope**: Summarize each exchange into 100-150 tokens, preserving key facts, emotions, and decisions.
- Store both LLM-generated `summary` and raw `full_text` (for later analysis).

### 1.6 Configuration & Feature Flags [NEW]
- Add `memory` section to `config.json` with budget limits (`max_active`, `token_limit`) and feature flags (+ embedding fallback).

---

## Phase 2: Intelligence & Gating
Goal: Filter what is remembered and manage the long-term memory budget.

### 2.1 Memory Write Gates [NEW]
- Implement gating (explicit request, high emotion, etc.) with structured logging for transparency.

### 2.2 Importance Scoring (with Decay) [NEW]
- Implement `calculate_importance()` with time-based decay.

### 2.3 Hybrid Retrieval (Over-fetch & Rerank) [MODIFY]
- **Formula**: `relevance = similarity * 0.5 + importance * 0.3 + recency * 0.2`.
- Rerank vector search candidates (top 20) before injecting into context.

### 2.4 Batched Memory Budget [NEW]
- Check budget every 50 episodes. Archive (status='archived') oldest/lowest-relevance items exceeding limits.

---

## Phase 3: Semantic, Relational & Continuity
Goal: Deepen Miyori's history with fact extraction and background maintenance.

### 3.1 Batched Semantic Extraction [NEW]
- Extract facts during consolidation by batching multiple episodes in one LLM call.

### 3.2 Relational Memory (Conservative Updates) [NEW]
- Analyze communication patterns every 10 interactions; update base style slowly.

### 3.3 Contradiction Detection & Passive Confirmation [NEW]
- Detect fact conflicts; use natural "passive mentions" to resolve with the user.

### 3.4 Periodic Consolidation (Background) [NEW]
- Nightly task for clustering, fact extraction, and importance pruning.

---

## Verification Plan

### Automated Tests
- `tests/test_embedding_queue.py`: Verify episodes move from `pending` to `active`.
- `tests/test_context_budget.py`: Verify priority ordering respects 1000-token limit.
- `tests/test_summarization.py`: Verify LLM summary quality vs raw text.

### Manual Verification
1. **Immediate Response**: Verify TTS starts before embedding/summary finishes.
2. **Persistence**: Verify Miyori's personality (Relational context) stays consistent across restarts.
3. **Budget Stress**: Fill context with 50+ matches; verify high-priority facts are kept over low-relevance episodes.
