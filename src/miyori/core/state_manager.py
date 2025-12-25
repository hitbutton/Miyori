from enum import Enum
from threading import Lock
from typing import Optional

class SystemState(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    SPEAKING = "speaking"

class StateManager:
    def __init__(self):
        self._state = SystemState.IDLE
        self._lock = Lock()
        self._interrupt_flag = False
    
    def get_state(self) -> SystemState:
        with self._lock:
            return self._state
    
    def transition_to(self, new_state: SystemState) -> bool:
        """Attempt state transition. Returns True if successful."""
        with self._lock:
            self._state = new_state
            return True
    
    def can_accept_input(self, is_text: bool) -> bool:
        """Check if input can be accepted."""
        with self._lock:
            if self._state == SystemState.IDLE:
                return True
            if is_text and self._state == SystemState.SPEAKING:
                return True  # Text can interrupt speech
            return False
    
    def request_interrupt(self) -> None:
        """Set interrupt flag for LLM to check."""
        with self._lock:
            self._interrupt_flag = True
    
    def clear_interrupt(self) -> None:
        """Clear interrupt flag."""
        with self._lock:
            self._interrupt_flag = False
    
    def should_interrupt(self) -> bool:
        """Check if interrupt was requested."""
        with self._lock:
            return self._interrupt_flag
