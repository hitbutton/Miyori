from dataclasses import dataclass, field
from typing import List, Optional

class AgenticExitSignal(BaseException):
    """Signal raised to exit an agentic loop."""
    def __init__(self, result: str, status: str):
        self.result = result
        self.status = status
        super().__init__(f"Agentic loop exit: {status} - {result}")

@dataclass
class AgenticState:
    """Tracks state for a multi-step agentic loop."""
    is_active: bool = False
    original_prompt: str = ""
    objective: str = ""
    iteration: int = 0
    max_iterations: int = 25
    working_directory: str = ""
    last_command: str = ""
    last_output: str = ""  # Truncated diagnostic output
    last_exit_code: Optional[int] = None
    modified_files: List[str] = field(default_factory=list)
    terminal_session_open: bool = False
    
    def reset(self):
        """Reset state to idle."""
        self.is_active = False
        self.original_prompt = ""
        self.objective = ""
        self.iteration = 0
        self.working_directory = ""
        self.last_command = ""
        self.last_output = ""
        self.last_exit_code = None
        self.modified_files = []
        self.terminal_session_open = False
