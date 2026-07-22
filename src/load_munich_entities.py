import json
from pathlib import Path
from typing import Optional, Dict, Any

def load_munich_entities() -> Optional[Dict[str, Any]]:
    """
    Safely loads Munich entities JSON file with fallback search.
    Handles path resolution to avoid backslash escaping issues.
    """
    # Define the project root using raw string to prevent \ escape interpretation
    PROJECT_ROOT = Path(r'E:\munich_handbook_research')
    
    # Primary target filename
    PRIMARY_FILE = 'munich_entities.json'
    primary_path = PROJECT_ROOT / PRIMARY_FILE
    
    # Fallback pattern for similar files (e.g., mhn_entities.json, entities_cleaned.json)
    fallback_pattern = PROJECT_ROOT.glob('*.json')
    
    loaded_data: Optional[Dict[str, Any]] = None
    
    try:
        if primary_path.exists():
            print(f"✅ Loaded entities from primary path: {primary_path}")
            with open(primary_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
        else:
            # Fallback search for any JSON file in the directory
            found_files = list(fallback_pattern)
            if found_files:
                # Select the most likely candidate (e.g., containing 'entity' in name)
                candidates = [f for f in found_files if 'entity' in f.name.lower()]
                target_path = Path(candidates[0]) if candidates else found_files[0]
                
                print(f"⚠️ Warning: Primary file '{PRIMARY_FILE}' not found.")
                print(f"🔍 Using fallback file: {target_path}")
                
                with open(target_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
            else:
                # If no JSON files exist at all in the directory
                raise FileNotFoundError(
                    f"No JSON entity files found in {PROJECT_ROOT}"
                )

    except FileNotFoundError as e:
        print(f"❌ Error: Munich entities file not found at {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format in {primary_path}: {e}")
        return None
    
    return loaded_data

# Usage Example
if __name__ == "__main__":
    entities = load_munich_entities()
    if entities:
        # Proceed with disambiguation logic here
        print(f"Loaded {len(entities)} entities.")