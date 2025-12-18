import os
from pathlib import Path
from src.core.tools import Tool, ToolParameter

# Configuration - set allowed directories
# We'll resolve these relative to the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
ALLOWED_DIRECTORIES = [
    (PROJECT_ROOT / "workspace").resolve(), 
    (PROJECT_ROOT / "documents").resolve()
]

def _is_path_allowed(path: Path) -> bool:
    """Check if path is within allowed directories."""
    try:
        # Ensure the directory exists so resolve() works as expected for subpaths
        for allowed in ALLOWED_DIRECTORIES:
            allowed.mkdir(parents=True, exist_ok=True)
            
        resolved = path.resolve()
        return any(resolved == allowed or resolved.is_relative_to(allowed) for allowed in ALLOWED_DIRECTORIES)
    except (ValueError, RuntimeError):
        return False

def _read_file(path: str) -> str:
    """Read and return file contents."""
    target_path = Path(path)
    if not target_path.is_absolute():
        target_path = (PROJECT_ROOT / path).resolve()
    
    try:
        if not target_path.exists():
            return f"Error: File not found: {path}"
        
        if not target_path.is_file():
            return f"Error: Not a file: {path}"
        
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Limit content length
        if len(content) > 5000:
            content = content[:5000] + "\n... (truncated to 5000 chars)"
        
        return f"Contents of {target_path.name}:\n\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def _write_file(path: str, content: str) -> str:
    """Write content to a file."""
    target_path = Path(path)
    if not target_path.is_absolute():
        target_path = (PROJECT_ROOT / path).resolve()
    
    if not _is_path_allowed(target_path):
        return f"Error: Access denied. Write operations are restricted to allowed directories: {[str(d) for d in ALLOWED_DIRECTORIES]}"
    
    try:
        # Ensure parent directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✓ Successfully wrote {len(content)} characters to {target_path.name}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def _list_directory(path: str) -> str:
    """List directory contents."""
    target_path = Path(path)
    if not target_path.is_absolute():
        target_path = (PROJECT_ROOT / path).resolve()
    
    try:
        if not target_path.exists():
            return f"Error: Directory not found: {path}"
        
        if not target_path.is_dir():
            return f"Error: Not a directory: {path}"
        
        items = list(target_path.iterdir())
        
        result = f"Contents of {target_path}:\n"
        for item in sorted(items):
            prefix = "📁" if item.is_dir() else "📄"
            size = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
            result += f"\n{prefix} {item.name}{size}"
        
        if not items:
            result += "\n(Empty directory)"
            
        return result
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def file_operations(operation: str, path: str, content: str = None) -> str:
    """
    Perform file operations (read, write, or list).
    
    Args:
        operation: Either "read", "write", or "list"
        path: Path to the file or directory
        content: Content to write (only used for write operation)
    
    Returns:
        File contents, write confirmation, or directory listing
    """
    print(f"📁 File operation: {operation} {path}")
    
    if operation == "read":
        return _read_file(path)
    elif operation == "write":
        if content is None:
            return "Error: 'content' parameter required for write operation"
        return _write_file(path, content)
    elif operation == "list":
        return _list_directory(path)
    else:
        return f"Error: Unknown operation '{operation}'. Use 'read', 'write', or 'list'."


# Create the tool definition
file_ops_tool = Tool(
    name="file_operations",
    description=(
        "Interact with the filesystem. Read/List operations work anywhere on the system (C:/, G:/, etc.). "
        "Write operations are restricted to workspace/ or documents/.\n\n"
        "GUIDANCE FOR SPEECH INPUT:\n"
        "1. If the user mentions a drive letter (e.g., 'C drive', 'see Dr'), use the root path (e.g., 'C:/').\n"
        "2. INFER PATHS: If the user refers to a folder seen in a previous 'list' output, "
        "combine the previous path with the new folder name to create an absolute path.\n"
        "3. PROACTIVE: If the user is vague but context suggests a path, try the most likely path. "
        "You have full permission to explore the system for reading and listing."),
    parameters=[
        ToolParameter(
            name="operation",
            type="string",
            description="Operation to perform: 'read', 'write', or 'list'",
            required=True,
            enum=["read", "write", "list"]
        ),
        ToolParameter(
            name="path",
            type="string",
            description="File or directory path. Can be absolute (e.g., 'C:/Users/...') or relative to project root.",
            required=True
        ),
        ToolParameter(
            name="content",
            type="string",
            description="Content to write to file (only for write operation)",
            required=False
        )
    ],
    function=file_operations
)
