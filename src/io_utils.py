from pathlib import Path
import json
import logging
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AuditError(Exception):
    """Raised when an audit operation fails (e.g., invalid schema, missing provenance)."""
    pass

def load_json_safe(path: Path) -> Optional[Dict[str, Any]]:
    """Safely loads a JSON file. Returns None if not found or invalid."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError as e:
        logger.warning(f'{path} failed: File not found ({e})')
        return None
    except json.JSONDecodeError as e:
        logger.warning(f'{path} failed: Invalid JSON ({e})')
        return None
    except Exception as e:
        logger.error(f'{path} failed: Unexpected error ({type(e).__name__}: {e})')
        return None

def load_json_list_safe(path: Path) -> Optional[List[Any]]:
    """Safely loads a JSON file as a list. Returns empty list if not found or invalid."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError as e:
        logger.warning(f'{path} failed: File not found ({e})')
        return []
    except json.JSONDecodeError as e:
        logger.warning(f'{path} failed: Invalid JSON ({e})')
        return []
    except Exception as e:
        logger.error(f'{path} failed: Unexpected error ({type(e).__name__}: {e})')
        return []

def save_json_safe(path: Path, data: Any) -> bool:
    """Safely saves data to a JSON file. Creates parent directories if needed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f'Saved {path}')
        return True
    except Exception as e:
        logger.error(f'{path} failed: {type(e).__name__}: {e}')
        return False

def sanitize_entity(entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Sanitizes a single entity dictionary to ensure it is safe for serialization."""
    if 'category' not in entity or 'name' not in entity:
        logger.warning(
            f"Skipping record due to missing required keys: {entity.get('id', 'unknown')}. "
            f"Missing: category, name. Raw data: {entity}"
        )
        return None
    sanitized = entity.copy()
    string_fields = ['category', 'name', 'description', 'role', 'status', 'function']
    for field in string_fields:
        if field in sanitized and sanitized[field] is None:
            sanitized[field] = ""
    for key in ['examples', 'applies_to']:
        if key in sanitized and isinstance(sanitized[key], list):
            sanitized[key] = [(item if isinstance(item, str) else "") for item in sanitized[key]]
    return sanitized

def write_entities_safe(entities: List[Dict[str, Any]], output_path: Path) -> int:
    """Safely serializes a list of entities to JSON."""
    sanitized_entities = []
    skipped_count = 0
    for idx, entity in enumerate(entities):
        safe_entity = sanitize_entity(entity)
        if safe_entity is not None:
            sanitized_entities.append(safe_entity)
        else:
            skipped_count += 1
    total_count = len(entities)
    logger.info(
        f"Serialization complete. Total processed: {total_count}, "
        f"Skipped (invalid): {skipped_count}, "
        f"Written: {len(sanitized_entities)}."
    )
    if sanitized_entities:
        try:
            json_content = json.dumps(
                sanitized_entities, 
                indent=2, 
                ensure_ascii=False, 
                sort_keys=True
            )
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_content)
            logger.info(f"Successfully wrote {len(sanitized_entities)} entities to '{output_path}'.")
            return len(sanitized_entities)
        except Exception as e:
            logger.error(f"Failed to write entities to '{output_path}': {e}")
            return 0
    return 0
