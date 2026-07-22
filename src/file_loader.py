import json
from pathlib import Path
from typing import Any, Optional

# Custom exception for descriptive file loading errors
class FileLoadError(Exception):
    """Raised when a file fails to load due to structural or permission issues."""
    pass

def safe_load_json(path: str) -> Optional[dict[str, Any]]:
    """
    Attempts to load a JSON file safely. Returns None if the file 
    does not exist, is empty, or contains invalid JSON.
    
    Use this when the application should continue gracefully without data.
    """
    path_obj = Path(path)
    
    # Check existence first to avoid FileNotFoundError noise
    if not path_obj.exists():
        return None
    
    try:
        with open(path_obj, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, PermissionError, UnicodeDecodeError) as e:
        # Log error internally or to a logger in production
        print(f"Failed to load {path}: {e}")
        return None

def load_json(path: str, strict: bool = True) -> dict[str, Any]:
    """
    Loads a JSON file with strict validation. Raises FileLoadError 
    if the file is missing or invalid.
    
    Args:
        path: Path to the JSON file.
        strict: If True (default), raises exceptions. If False, returns None on failure.
        
    Returns:
        Parsed dictionary or None (if strict=False).
        
    Raises:
        FileLoadError: If file is missing, unreadable, or invalid JSON.
    """
    path_obj = Path(path)
    
    # 1. Validate Path Existence
    if not path_obj.exists():
        raise FileLoadError(f"File not found: {path}")
    
    # 2. Validate Read Permissions (Audit/Security check)
    if not path_obj.is_file():
        raise FileLoadError(f"Path is not a file: {path}")

    try:
        with open(path_obj, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 3. Basic Schema Validation (Optional but recommended for production)
        if not isinstance(data, dict):
            raise FileLoadError(f"Expected JSON object at {path}, got {type(data).__name__}")
            
        return data
        
    except PermissionError:
        raise FileLoadError(f"Permission denied reading file: {path}")
    except UnicodeDecodeError:
        raise FileLoadError(f"Invalid encoding detected in file: {path}. Expected UTF-8.")
    except json.JSONDecodeError as e:
        raise FileLoadError(f"Invalid JSON syntax at line {e.lineno}: {e.msg}")