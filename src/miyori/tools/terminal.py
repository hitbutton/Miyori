import subprocess
import os
import re
from typing import Dict, Any, List, Optional, Callable
from miyori.core.tools import Tool, ToolParameter
from miyori.utils.config import Config
from miyori.core.agentic_state import AgenticState

class TerminalManager:
    """Manages terminal execution and state for the persistent session."""
    def __init__(self, agentic_state: AgenticState, approval_callback: Optional[Callable[[str], bool]] = None):
        self.agentic_state = agentic_state
        self.approval_callback = approval_callback
        self.cwd = os.getcwd()
        self.dangerous_patterns = Config.data.get("tools", {}).get("terminal", {}).get("dangerous_patterns", [])
        self.timeout = Config.data.get("tools", {}).get("terminal", {}).get("timeout_seconds", 120)

    def execute(self, command: str, persistent: bool = False, close: bool = False) -> str:
        if close:
            self.agentic_state.terminal_session_open = False
            return "Persistent terminal session closed."

        if persistent:
            self.agentic_state.terminal_session_open = True
            
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command):
                if self.approval_callback:
                    approved = self.approval_callback(command)
                    if not approved:
                        return f"Command rejected by user: {command}"
                else:
                    return f"Potentially dangerous command blocked (no approval mechanism): {command}"

        # Handle 'cd' manually for persistence
        if command.startswith("cd "):
            new_path = command[3:].strip().replace('"', '').replace("'", "")
            abs_path = os.path.abspath(os.path.join(self.cwd, new_path))
            if os.path.isdir(abs_path):
                self.cwd = abs_path
                self.agentic_state.working_directory = self.cwd
                return f"Changed directory to: {self.cwd}"
            else:
                return f"Error: Directory not found: {new_path}"

        try:
            # Execute command
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=self.cwd,
                timeout=self.timeout
            )
            
            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr
            
            # Update state
            self.agentic_state.last_command = command
            self.agentic_state.last_exit_code = result.returncode
            # Truncate output for state tracking (~500 chars)
            self.agentic_state.last_output = output[:500] + ("..." if len(output) > 500 else "")
            
            return output if output else f"Command executed successfully (no output). Exit code: {result.returncode}"
            
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {self.timeout} seconds."
        except Exception as e:
            return f"Error executing command: {str(e)}"

def create_terminal_tool(agentic_state: AgenticState, approval_callback: Optional[Callable[[str], bool]] = None) -> Tool:
    manager = TerminalManager(agentic_state, approval_callback)
    
    def terminal(command: str = "", persistent: bool = False, close: bool = False) -> str:
        """Entry point for the terminal tool."""
        if not command and not close:
            return "Error: No command provided."
        return manager.execute(command, persistent, close)

    return Tool(
        name="terminal",
        description="Execute shell commands in the local environment. Use persistent=True to maintain CWD across calls.",
        parameters=[
            ToolParameter(name="command", type="string", description="The shell command to execute.", required=False),
            ToolParameter(name="persistent", type="boolean", description="If True, maintains working directory for future calls.", required=False),
            ToolParameter(name="close", type="boolean", description="Close the persistent session.", required=False)
        ],
        function=terminal
    )
