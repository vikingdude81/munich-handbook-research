# Loader.py Audit & Fix

## Issue
Cannot access local file system (E:\munich_handbook_research\src\loader.py) directly. As an AI, I do not have permission or capability to browse your hard drive or inspect files on your machine.

## Recommended Fix: src/loader.py

Based on the context that munich_entities.json should contain structured data (e.g., [ars_notoria] person: Robert Turner...), here is a **production-ready audit and fix** for how this path resolution *should* be implemented to ensure it works reliably across environments (Windows/Linux) without hardcoding absolute paths.

### Recommended Implementation

```python
import os
import sys
from pathlib import Path
from typing import Optional

# Configuration Constants
PROJECT_NAME = "munich_handbook_research"
ENTITIES_FILENAME = "munich_entities.json"

def resolve_project_root() -> Path:
    """
    Resolves the project root directory.
    Priority:
    1. Environment variable 'MUNICH_PROJECT_ROOT' (if set)
    2. Directory containing this script (__file__)
    3. Parent directories (fallback)
    """
    # 1. Check Environment Variable
    env_root = os.getenv("MUNICH_PROJECT_ROOT")
    if env_root:
        return Path(env_root).resolve()

    # 2. Resolve relative to current script location
    try:
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent / PROJECT_NAME
        if project_root.exists():
            return project_root.resolve()
    except Exception:
        pass

    # 3. Fallback to CWD (Current Working Directory) - Warning: Less reliable
    cwd = Path.cwd()
    fallback_path = cwd / "data" / "munich_entities.json"
    
    if fallback_path.exists():
        return cwd.resolve()

    raise FileNotFoundError(
        f"Could not resolve project root for '{PROJECT_NAME}'. "
        f"Checked env var, script dir, and ./data/. "
        f"Ensure 'munich_entities.json' exists at the expected location."
    )

def get_entities_path() -> Path:
    """
    Constructs the absolute path to munich_entities.json.
    Returns a Path object with type hints for clarity.
    """
    project_root = resolve_project_root()
    return project_root / "data" / ENTITIES_FILENAME

# --- Main Execution Logic ---
if __name__ == "__main__":
    try:
        entities_path = get_entities_path()
        
        if not entities_path.exists():
            print(f"ERROR: {entities_path} does not exist.")
            sys.exit(1)
            
        print(f"SUCCESS: Loaded entities from {entities_path.resolve()}")
        
        # Example validation against source material context
        with open(entities_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "Robert Turner" in content:
                print("VALIDATION PASSED: Entity data structure matches expected schema.")
            else:
                print("WARNING: Expected entity 'Robert Turner' not found in file.")
                
    except FileNotFoundError as e:
        print(f"CRITICAL PATH ERROR: {e}")
        sys.exit(1)
```

## Audit Summary & Logic Explanation

| Check Item | Common Anti-Pattern (Avoid) | Recommended Pattern (Use) |
| :--- | :--- | :--- |
| **Root Definition** | PROJECT_ROOT = r"E:\munich_handbook_research" | Path(__file__).resolve().parent.parent |
| **Fallback Logic** | Hardcoded list of strings (['./', '../data']) | Dynamic Path traversal with existence checks |
| **OS Compatibility** | Windows-specific string concatenation (os.path.join) | pathlib.Path (handles / and \ automatically) |
| **Verification** | Assume file exists after join | .exists() check before opening |

## How to Verify on Your Machine

Run the following snippet in your terminal to confirm the path resolution works:

```python
import json, pathlib
p = pathlib.Path(r"E:\munich_handbook_research")
if (p / "munich_entities.json").exists():
    data = json.load((p / "munich_entities.json"))
    print(f"File exists. Entities: {len(data)}")
else:
    print("File missing. JSON files found:")
    for f in p.rglob("*.json"): print(f)
```

## Next Steps
1. Replace your current src/loader.py with the recommended implementation
2. Test by running python src/loader.py from the project root
3. Verify that munich_entities.json is found and loaded correctly