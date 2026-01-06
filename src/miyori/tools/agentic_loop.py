from typing import Dict, Any
from miyori.core.tools import Tool, ToolParameter
from miyori.core.agentic_state import AgenticState

def create_agentic_loop_tool(agentic_state: AgenticState) -> Tool:
    """Creates the agentic_loop tool with shared state access."""
    
    def agentic_loop(objective: str, user_prompt: str = "") -> str:
        """Initialize the agentic loop state."""
        agentic_state.is_active = True
        agentic_state.objective = objective
        if user_prompt:
            agentic_state.original_prompt = user_prompt
        agentic_state.iteration = 1
        
        return f"Agentic loop initialized. Objective: {objective}. Entering autonomous mode."

    return Tool(
        name="agentic_loop",
        description="Switch to autonomous agentic mode to pursue a multi-step objective without further user input.",
        parameters=[
            ToolParameter(
                name="objective",
                type="string",
                description="The clear, specific goal you are going to pursue autonomously.",
                required=True
            ),
            ToolParameter(
                name="user_prompt",
                type="string",
                description="The original user request that triggered this objective (optional).",
                required=False
            )
        ],
        function=agentic_loop
    )
