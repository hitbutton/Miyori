# Human-Like Memory System Design

## Overview

This system simulates human-like memory through multi-tiered storage, semantic associations, and continuous narrative editing. The goal is **behavioral consistency** and **engaging interaction**, not eidetic recall.

### Core Principle
> *"Human-like memory is a continuously edited narrative optimized for future interaction"*

Memory exists to:
- **Episodic**: Teach the system through experiences
- **Semantic**: Guide future behavior with distilled knowledge
- **Relational**: Maintain consistent personality and interaction style

---

## Architecture

### Four-Tier Memory System

```
Raw Logs (temporary)
    ↓ (immediate processing)
Episodic Memory (conversations)
    ↓ (consolidation)
Semantic Memory (facts/knowledge)
    ↓ (behavioral priors)
Relational Memory (personality/interaction norms)
```

---

## Storage Formats

### 1. Episodic Memory (Conversations)

```json
{
  "id": "uuid",
  "timestamp": "2024-11-15T14:30:00Z",
  "summary": "User discussed anxiety about job interview at TechCorp",
  "embedding": [0.123, -0.456, ...],
  "importance": 0.85,
  "emotional_valence": -0.3,
  "topics": ["career", "anxiety"],
  "entities": ["TechCorp", "Sarah (friend)"],
  "connections": ["uuid2", "uuid5"],
  "status": "active"
}
```

**Fields:**
- `embedding`: 1536-dim vector for semantic similarity search
- `importance`: 0-1 scale, calculated at write time, decays over time
- `emotional_valence`: -1 (negative) to +1 (positive)
- `connections`: UUIDs of related memories
- `status`: `active|archived|deprecated`

### 2. Semantic Memory (Facts)

```json
{
  "fact": "Works as software engineer",
  "confidence": 0.95,
  "first_observed": "2024-01-15T10:00:00Z",
  "last_confirmed": "2024-11-02T15:30:00Z",
  "version_history": [
    {
      "fact": "Computer science student",
      "retired": "2024-01-15T10:00:00Z",
      "reason": "graduated"
    }
  ],
  "derived_from": ["uuid1", "uuid3", "uuid7"],
  "contradictions": [],
  "status": "stable"
}
```

**Status Values:**
- `tentative`: Needs more evidence
- `stable`: Repeatedly confirmed
- `deprecated`: Superseded by newer information

### 3. Relational Memory (Interaction Norms)

```json
{
  "interaction_norms": {
    "communication_style": {
      "value": "direct, systems-oriented, appreciates technical depth",
      "confidence": 0.85,
      "evidence_count": 12,
      "last_updated": "2024-11-15T09:00:00Z"
    },
    "preferences": {
      "prefers_direct_answers": true,
      "dislikes_excessive_validation": true,
      "enjoys_systems_thinking": true
    },
    "sensitivity_map": {
      "work_stress": 0.7,
      "family_topics": 0.3,
      "health_concerns": 0.8
    },
    "relationship_phase": "established_trust"
  }
}
```

**Relationship Phases:**
- `early`: First few interactions
- `building`: Establishing patterns
- `established_trust`: Consistent, comfortable interaction

### 4. Emotional Continuity (Thread Tracking)

```json
{
  "emotional_thread": {
    "current_state": "excited about new project",
    "recognized_from": ["uuid_recent_1", "uuid_recent_2"],
    "should_acknowledge": true,
    "thread_length": 3,
    "last_update": "2024-11-15T14:00:00Z"
  }
}
```

---

## Memory Write Gate

Not everything should be remembered. Use explicit gates:

```python
def should_remember(conversation_turn):
    """
    Decide if a conversation turn should be stored.
    Must pass at least one positive gate + harm check.
    """
    gates = {
        # Positive gates (at least one must be True)
        'explicit_request': user_said("remember this"),
        'relational_damage': would_hurt_to_forget(),
        'identity_defining': is_about_core_self(),
        'stable_fact': not_situational_mood(),
        'high_emotion': abs(emotional_valence) > 0.6,
        'decision_made': user_made_commitment(),
        
        # Required gate (must always be True)
        'harm_check': not_sensitive_or_biased()
    }
    
    positive = any([
        gates['explicit_request'],
        gates['relational_damage'],
        gates['identity_defining'],
        gates['high_emotion'],
        gates['decision_made']
    ])
    
    return positive and gates['harm_check']
```

**Critical Questions:**
- Would forgetting cause relational damage?
- Is this stable over time or a transient state?
- Is this identity-defining or situational?
- Would remembering cause harm or encode bias?

---

## Importance Scoring

Human memory prioritizes emotional, personal, and decision-based content:

```python
import math
from datetime import datetime, timedelta

def calculate_importance(conversation):
    """
    Calculate importance score with time-based decay.
    Returns 0-1 float.
    """
    score = 0.5  # baseline
    
    # Boost factors (cumulative)
    if conversation.emotional_content:
        score += 0.3
    if conversation.user_shared_personal:
        score += 0.2
    if conversation.user_made_decision:
        score += 0.2
    if conversation.user_asked_to_remember:
        score += 0.4
    if conversation.referenced_multiple_times:
        score += 0.1 * conversation.reference_count
    if conversation.involved_conflict_resolution:
        score += 0.25
    
    # Cap at 1.0
    score = min(score, 1.0)
    
    # Time decay (slower for high importance)
    age_days = (datetime.now() - conversation.timestamp).days
    half_life = 100 * score  # high importance decays slower
    decay = math.exp(-age_days * math.log(2) / half_life)
    
    return score * decay
```

---

## Hybrid Retrieval System

Combine semantic similarity with symbolic filtering:

```python
def retrieve_memories(query, max_results=5):
    """
    Two-stage retrieval: vector search + symbolic pruning.
    """
    # Stage 1: Semantic similarity (cast wide net)
    query_embedding = embed(query)
    candidates = vector_search(
        query_embedding,
        memory_db,
        top_k=20  # Overfetch for filtering
    )
    
    # Stage 2: Symbolic pruning
    now = datetime.now()
    filtered = []
    
    for memory in candidates:
        # Skip deprecated memories
        if memory.status == 'deprecated':
            continue
        
        # Calculate relevance score
        age_days = (now - memory.timestamp).days
        recency_weight = 1.0 / (1 + age_days / 30)  # Decay over ~month
        
        relevance = (
            memory.importance * 0.5 +
            recency_weight * 0.3 +
            memory.similarity_score * 0.2
        )
        
        # Threshold filter
        if relevance > 0.4:
            filtered.append((memory, relevance))
    
    # Stage 3: Budget enforcement
    filtered.sort(key=lambda x: x[1], reverse=True)
    return [m for m, _ in filtered[:max_results]]
```

### Additional Filters

```python
def apply_context_filters(memories, current_context):
    """Apply context-aware filtering."""
    filtered = []
    
    for memory in memories:
        # Emotional polarity matching
        if current_context.emotional_valence:
            valence_diff = abs(
                memory.emotional_valence - 
                current_context.emotional_valence
            )
            if valence_diff > 1.0:  # Opposite emotions
                continue
        
        # Topic compatibility
        if current_context.topics:
            topic_overlap = set(memory.topics) & set(current_context.topics)
            if not topic_overlap and memory.importance < 0.7:
                continue
        
        filtered.append(memory)
    
    return filtered
```

---

## Contradiction Detection & Resolution

```python
def handle_new_memory(new_memory):
    """
    Detect and resolve conflicts with existing semantic memories.
    """
    # Find potential conflicts
    conflicts = find_semantic_conflicts(new_memory)
    
    for old_memory in conflicts:
        # Newer information takes precedence
        if new_memory.timestamp > old_memory.last_confirmed:
            # Reduce confidence in old memory
            old_memory.confidence *= 0.7
            
            # Link memories
            old_memory.contradictions.append(new_memory.id)
            new_memory.contradictions.append(old_memory.id)
            
            # Mark as needing confirmation
            old_memory.status = 'tentative'
        
        # High-importance conflicts need user confirmation
        if old_memory.importance > 0.8:
            flag_for_confirmation(old_memory, new_memory)

def flag_for_confirmation(old_mem, new_mem):
    """
    Prompt user to resolve important conflicts.
    """
    prompt = (
        f"I remember {old_mem.fact}, but you just mentioned {new_mem.fact}. "
        f"Which is current?"
    )
    # Queue for next interaction
    add_to_pending_clarifications(prompt)
```

---

## Context Assembly

```python
def build_context(user_message):
    """
    Assemble context from multiple memory tiers.
    """
    # 1. Relevant episodic memories (semantic search)
    relevant_episodes = retrieve_memories(user_message, max_results=3)
    
    # 2. Recent high-importance memories
    recent_important = get_recent_memories(
        days=7,
        min_importance=0.7,
        limit=2
    )
    
    # 3. Active semantic facts
    user_facts = get_active_semantic_facts(
        confidence_threshold=0.7,
        limit=5
    )
    
    # 4. Relational norms
    interaction_style = get_relational_memory()
    
    # 5. Emotional continuity
    emotional_thread = get_current_emotional_thread()
    
    # Assemble natural language context
    context = f"""
INTERACTION STYLE: {interaction_style.communication_style.value}

CURRENT EMOTIONAL THREAD: {emotional_thread.current_state if emotional_thread else "None"}

USER FACTS:
{format_facts(user_facts)}

RECENT IMPORTANT:
{format_episodes(recent_important)}

RELEVANT PAST:
{format_episodes(relevant_episodes)}
"""
    
    return context
```

---

## Consolidation Process

Run periodically (daily/weekly) to compress and distill memories:

```python
def consolidate_memories():
    """
    Consolidation goal: Reduce episodic load while strengthening
    semantic knowledge and preserving emotional landmarks.
    """
    old_episodes = get_episodes(older_than_days=30, status='active')
    
    # 1. Cluster related episodes by semantic similarity
    clusters = cluster_by_embedding(old_episodes, min_cluster_size=3)
    
    for cluster in clusters:
        # 2. Extract stable facts
        semantic_facts = extract_semantic_facts(cluster)
        for fact in semantic_facts:
            upsert_semantic_memory(fact)
        
        # 3. Preserve emotional landmarks
        emotional_peaks = [
            e for e in cluster 
            if abs(e.emotional_valence) > 0.6 or e.importance > 0.8
        ]
        for episode in emotional_peaks:
            episode.status = 'archived'  # Keep but mark as old
        
        # 4. Compress the rest
        mundane_episodes = [
            e for e in cluster 
            if e not in emotional_peaks
        ]
        
        if mundane_episodes:
            summary = create_cluster_summary(mundane_episodes)
            archive_episodes(mundane_episodes, summary)

def extract_semantic_facts(episode_cluster):
    """
    Find stable, repeated patterns across episodes.
    """
    facts = []
    
    # Example: If user mentions same fact 3+ times
    fact_counts = count_repeated_facts(episode_cluster)
    
    for fact, count in fact_counts.items():
        if count >= 3:
            facts.append({
                'fact': fact,
                'confidence': min(count / 10, 1.0),
                'derived_from': [e.id for e in episode_cluster],
                'first_observed': min(e.timestamp for e in episode_cluster),
                'status': 'stable'
            })
    
    return facts
```

---

## Memory Budget Enforcement

Hard limits prevent unbounded growth:

```python
class MemoryBudget:
    """Enforce hard limits on memory tiers."""
    
    LIMITS = {
        'episodic_active': 1000,      # Recent conversations
        'episodic_archived': 5000,    # Compressed old episodes
        'semantic_facts': 500,
        'relational_norms': 50        # Slowly changing
    }
    
    def enforce(self):
        """Prune least important memories when over budget."""
        
        # Episodic: Keep recent + high importance
        active_episodes = get_all_episodes(status='active')
        if len(active_episodes) > self.LIMITS['episodic_active']:
            # Sort by: recency * importance
            ranked = sorted(
                active_episodes,
                key=lambda e: self.score_episode(e),
                reverse=True
            )
            
            # Keep top N
            keep = ranked[:self.LIMITS['episodic_active']]
            archive = ranked[self.LIMITS['episodic_active']:]
            
            for episode in archive:
                episode.status = 'archived'
        
        # Semantic: Merge similar facts, prune low confidence
        self.consolidate_semantic_facts()
    
    def score_episode(self, episode):
        """Combined recency + importance score."""
        age_days = (datetime.now() - episode.timestamp).days
        recency = 1.0 / (1 + age_days / 30)
        return episode.importance * 0.6 + recency * 0.4
```

---

## Implementation Stack

### Embeddings
- **API**: OpenAI `text-embedding-3-small` (1536 dims)
- **Local**: `sentence-transformers/all-MiniLM-L6-v2` (384 dims)

### Vector Storage
- **Simple**: NumPy arrays + cosine similarity
- **Scalable**: Chroma, Pinecone, or FAISS

### Database
- **SQLite** with JSON columns for structured data
- Separate tables for each memory tier

### Example Schema

```sql
CREATE TABLE episodic_memory (
    id TEXT PRIMARY KEY,
    timestamp DATETIME,
    summary TEXT,
    embedding BLOB,  -- pickled numpy array
    importance REAL,
    emotional_valence REAL,
    topics JSON,
    entities JSON,
    connections JSON,
    status TEXT
);

CREATE TABLE semantic_memory (
    id TEXT PRIMARY KEY,
    fact TEXT,
    confidence REAL,
    first_observed DATETIME,
    last_confirmed DATETIME,
    version_history JSON,
    derived_from JSON,
    contradictions JSON,
    status TEXT
);

CREATE TABLE relational_memory (
    id TEXT PRIMARY KEY,
    category TEXT,  -- 'communication_style', 'preferences', etc.
    data JSON,
    confidence REAL,
    evidence_count INTEGER,
    last_updated DATETIME
);
```

---

## Implementation Priority

Build incrementally in this order:

### Phase 1: Foundation (MVP)
1. Basic episodic storage with timestamps
2. Simple embedding-based retrieval
3. Hard memory budget (top-K recent + important)

### Phase 2: Intelligence
4. Memory write gates
5. Importance scoring with decay
6. Hybrid retrieval (vector + symbolic)

### Phase 3: Personality
7. Relational memory layer
8. Emotional continuity tracking
9. Interaction style consistency

### Phase 4: Self-Correction
10. Semantic versioning
11. Contradiction detection
12. User confirmation prompts

### Phase 5: Optimization
13. Consolidation with explicit goals
14. Advanced clustering
15. Retrieval transparency logging (for debugging)

---

## Key Design Principles

1. **Forget Aggressively**: Human memory is lossy by design
2. **Prioritize Relationships**: Interaction norms > raw facts
3. **Version Everything**: Facts change, track history
4. **Budget Ruthlessly**: Hard limits prevent bloat
5. **Emotional Weight**: High-emotion memories persist longer
6. **Continuous Editing**: Memory is narrative, not archive
7. **Conservative Updates**: Relational changes require repeated evidence

---

## Debugging & Monitoring

Add logging for:

```python
def log_retrieval_decision(memory, reason):
    """Track why memories were retrieved (for debugging)."""
    log = {
        'memory_id': memory.id,
        'similarity_score': memory.similarity_score,
        'importance': memory.importance,
        'age_days': memory.age_days,
        'reason': reason,  # 'high_similarity', 'recent_important', etc.
        'timestamp': datetime.now()
    }
    append_to_debug_log(log)
```

Monitor:
- Retrieval hit rate (% queries finding relevant memories)
- Average memory age at retrieval
- Contradiction frequency
- Consolidation compression ratio

---

## Example Interaction Flow

```python
def handle_user_message(message):
    # 1. Retrieve relevant context
    context = build_context(message)
    
    # 2. Generate response with context
    response = generate_response(message, context)
    
    # 3. Decide if conversation should be remembered
    if should_remember(message, response):
        # 4. Calculate importance
        importance = calculate_importance(message, response)
        
        # 5. Store episodic memory
        memory = create_episodic_memory(
            message,
            response,
            importance,
            embedding=embed(message)
        )
        store_memory(memory)
        
        # 6. Update emotional thread
        update_emotional_continuity(memory)
        
        # 7. Check for semantic facts
        facts = extract_facts(message)
        for fact in facts:
            upsert_semantic_memory(fact)
    
    # 8. Enforce budget
    if should_consolidate():
        consolidate_memories()
    
    return response
```

---

## Final Notes

This system trades **perfect recall** for **human-like engagement**. It:

- Forgets mundane details naturally
- Remembers emotionally significant moments
- Maintains behavioral consistency
- Self-corrects when wrong
- Adapts interaction style slowly

The goal is a memory system that feels like talking to someone who knows you, not querying a database.