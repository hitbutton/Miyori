import asyncio
from typing import Set, AsyncGenerator
from miyori.core.state_manager import SystemState

class SSEManager:
    def __init__(self):
        self._clients: Set[asyncio.Queue] = set()
    
    async def event_generator(self) -> AsyncGenerator[dict, None]:
        """Generator for SSE events."""
        queue = asyncio.Queue()
        self._clients.add(queue)
        
        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            self._clients.remove(queue)
    
    async def broadcast_state(self, state: SystemState):
        """Broadcast state change to all clients."""
        event = {
            "event": "state",
            "data": state.value
        }
        await self._broadcast(event)
    
    async def broadcast_chunk(self, chunk: str):
        """Broadcast response chunk to all clients."""
        event = {
            "event": "chunk",
            "data": chunk
        }
        await self._broadcast(event)
    
    async def _broadcast(self, event: dict):
        """Send event to all connected clients."""
        # Create tasks for all clients to broadcast concurrently
        tasks = []
        for queue in list(self._clients): # Use list to avoid modification during iteration
            tasks.append(asyncio.create_task(queue.put(event)))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
