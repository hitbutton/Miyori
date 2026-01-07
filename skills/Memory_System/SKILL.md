# Skill: Memory System & Retrieval

Miyori's memory is split into two main layers: **Episodic** (short-term conversations) and **Semantic** (long-term facts and models).

## Memory Layers

### 1. Episodic Memory
- **Purpose**: Stores individual conversation turns (episodes).
- **Structure**: `full_text`, `topics`, `entities`, `connections`, and an `embedding`.
- **Status**: New episodes start as `active`. Once processed, they are marked as `consolidated`.

### 2. Semantic Memory
- **Purpose**: Stores persistent facts, preferences, and models of the world/user.
- **Structure**: `fact_text`, `confidence` score (0.0 to 1.0), `status` (experimental, stable, archived), and `embedding`.
- **Merging**: Contradictory or redundant facts are merged using a `ConfidenceManager`.

## Retrieval Mechanism (`MemoryRetriever`)

When a user speaks, the `LLMCoordinator` requests a "Context" which is built using:
1. **Vector Search**: Finds relevant episodes and facts using cosine similarity on embeddings.
2. **Diversity Sampling**: Uses K-Means clustering to ensure the top results aren't just redundant copies of the same information.
3. **Prompt Injection**: The most relevant/diverse snippets are prepended to the user's prompt as "Memory Context".

## Consolidation (`EpisodeClustering`)

A background process (or triggered task) periodically turns episodes into facts:
1. **Clustering**: Uses **HDBSCAN** to group related conversation episodes together.
2. **Extraction**: An LLM analyzes each cluster to extract new semantic facts or update existing ones.
3. **Cleanup**: Original episodes are marked as consolidated to prevent redundant processing.

## How to use Memory Tools
- `memory_search`: Allows the agent to manually query either episodic or semantic memory with a text string.
- The search returns a list of matching entries with their text and metadata.
