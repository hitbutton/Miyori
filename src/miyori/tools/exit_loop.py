from typing import Dict, Any
from miyori.core.tools import Tool, ToolParameter
from miyori.core.agentic_state import AgenticExitSignal

def _exit_loop(result: str, status: str) -> str:
    """Exit the agentic loop with a result."""
    raise AgenticExitSignal(result=result, status=status)

exit_loop_tool = Tool(
    name="exit_loop",
    description="Exit the current agentic loop with a final result summary and status.",
    parameters=[
        ToolParameter(
            name="result",
            type="string",
            description="Summary of what was accomplished during the agentic session.",
            required=True
        ),
        ToolParameter(
            name="status",
            type="string",
            description="Overall success status of the objective.",
            required=True,
            enum=["success", "failure", "partial"]
        )
    ],
    function=_exit_loop
)
