import asyncio
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.memory.memory_retriever import MemoryRetriever
from src.utils.embeddings import EmbeddingService
from src.utils.memory_logger import memory_logger

@dataclass
class MemoryCache:
    """Cache entry for passive memory retrieval."""
    episodic_memories: List[Dict[str, Any]]
    semantic_facts: List[Dict[str, Any]]
    context_embedding: List[float]  # Embedding of the context used to generate this cache
    timestamp: datetime
    turn_count: int  # How many turns this cache has been valid for

    def is_valid(self, current_context_embedding: List[float], max_turns: int = 5) -> bool:
        """Check if cache is still valid based on context similarity only."""
        # Turn count check is now done in _refresh_cache
        
        if not self.context_embedding or not current_context_embedding:
            return False

        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity

        vec1 = np.array(self.context_embedding).reshape(1, -1)
        vec2 = np.array(current_context_embedding).reshape(1, -1)

        similarity = cosine_similarity(vec1, vec2)[0][0]
        return similarity > 0.7

class AsyncMemoryStream:
    """
    Passive streaming memory retrieval that runs asynchronously in background.
    Pre-fetches memories for the next conversation turn based on up to the last 3 turns.
    """

    def __init__(
        self,
        retriever: MemoryRetriever,
        embedding_service: EmbeddingService,
        max_cache_turns: int = 5
    ):
        self.retriever = retriever
        self.embedding_service = embedding_service
        self.max_cache_turns = max_cache_turns

        # Cache for next turn's memories
        self._cache: Optional[MemoryCache] = None

        # Background task management
        self._task: Optional[asyncio.Task] = None
        self._running = False

        # Recent conversation context (rolling window)
        self._recent_turns: List[str] = []
        self._max_recent_turns = 3  # Keep up to last 3 turns (earliest to most recent)

        # Track changes for selective refreshing
        self._last_turns_state: List[str] = []

    async def start(self):
        """Start the background memory streaming."""
        if self._running:
            return
        self._running = True
        memory_logger.log_event("async_memory_stream_started")

    async def stop(self):
        """Stop the background memory streaming task."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        memory_logger.log_event("async_memory_stream_stopped")

    def add_turn_context(self, user_message: str, miyori_response: str):
        """
        Add recent conversation turn to context window.
        This triggers ONE background pre-fetch for the next turn.
        """
        turn_text = f"User: {user_message}\nMiyori: {miyori_response}"
        
        self._recent_turns.append(turn_text)
        if len(self._recent_turns) > self._max_recent_turns:
            self._recent_turns.pop(0)
        
        # Trigger ONE async refresh (fire and forget)
        if self._running:
            # Schedule in the background event loop
            asyncio.create_task(self.refresh_cache())

    def get_cached_memories(self) -> Optional[Dict[str, List[Dict[str, Any]]]]:
        """
        Get pre-fetched memories for current turn.
        Returns None if no valid cache available.
        """
        if not self._cache:
            return None
        memory_logger.log_event("cache not none")
        return {
                'episodic': self._cache.episodic_memories,
                'semantic': self._cache.semantic_facts
                }

    async def refresh_cache(self):
        """Refresh the memory cache based on current context."""
            # Check if current cache is still valid BEFORE refreshing
        if self._cache is not None:
            # Check turn limit
            if self._cache.turn_count >= self.max_cache_turns:
                memory_logger.log_event("cache_invalidated", {"reason": "turn_limit"})
            else:
                # Check context similarity
                context_text = " ".join(self._recent_turns)
                new_embedding = self.embedding_service.embed(context_text)
                memory_logger.log_event("context_embedded", {"context_text": context_text })
                
                if self._cache.is_valid(new_embedding, self.max_cache_turns):
                    # Cache still valid, don't refresh
                    memory_logger.log_event("cache_revalidated", {
                        "turn_count": self._cache.turn_count
                    })
                    return
                else:
                    memory_logger.log_event("cache_invalidated", {
                        "reason": "context_drift"
                    })
        try:
            context_text = " ".join(self._recent_turns)
            if not context_text.strip():
                return

            # Generate embedding for current context
            context_embedding = self.embedding_service.embed(context_text)

            # Search for memories (3-5 facts + 3-5 episodes)
            episodic_memories = self.retriever.search_memories(
                query_embedding=context_embedding,
                search_type='episodic',
                limit=5,  # 3-5 will be selected via diversity sampling
                filters={'status': 'active', 'confidence__gt': 0.5}
            )

            semantic_facts = self.retriever.search_memories(
                query_embedding=context_embedding,
                search_type='semantic',
                limit=5,  # 3-5 will be selected via diversity sampling
                filters={}
            )

            # Create new cache entry
            self._cache = MemoryCache(
                episodic_memories=episodic_memories,
                semantic_facts=semantic_facts,
                context_embedding=context_embedding,
                timestamp=datetime.now(),
                turn_count=0
            )

            memory_logger.log_event("cache_refreshed", {
                "episodic_count": len(self._cache.episodic_memories),
                "semantic_count": len(self._cache.semantic_facts),
                "context_length": len(context_text)
            })

        except Exception as e:
            memory_logger.log_event("cache_refresh_error", {"error": str(e)})
