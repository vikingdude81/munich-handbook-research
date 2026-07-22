import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging to capture skipped records without cluttering the console excessively
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sanitize_entity(entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Sanitizes a single entity dictionary to ensure it is safe for serialization.
    
    1. Ensures required keys ('category', 'name') exist; if missing, returns None.
    2. Converts any None values in string fields to empty strings.
    3. Returns the sanitized dict or None if validation fails.
    
    Args:
        entity (Dict[str, Any]): The raw entity dictionary from the source data.
        
    Returns:
        Optional[Dict[str, Any]]: The sanitized dictionary, or None if invalid.
    """
    # Check for required keys
    if 'category' not in entity or 'name' not in entity:
        logger.warning(
            f"Skipping record due to missing required keys: {entity.get('id', 'unknown')}. "
            f"Missing: category, name. Raw data: {entity}"
        )
        return None

    # Create a copy to avoid mutating the original source data
    sanitized = entity.copy()

    # Define fields that should be strings and handle None values
    string_fields = ['category', 'name', 'description', 'role', 'status', 'function']
    
    for field in string_fields:
        if field in sanitized and sanitized[field] is None:
            sanitized[field] = ""

    # Handle specific complex fields like 'examples' or 'applies_to' which might contain None
    # We ensure list items are strings, replacing None with empty string within the list
    for key in ['examples', 'applies_to']:
        if key in sanitized and isinstance(sanitized[key], list):
            sanitized[key] = [
                (item if isinstance(item, str) else "") 
                for item in sanitized[key]
            ]

    return sanitized


def write_entities_safe(entities: List[Dict[str, Any]], output_path: Path) -> int:
    """
    Safely serializes a list of entities to JSON.
    
    Performs defensive checks on every entity before encoding.
    Logs statistics regarding skipped records.
    
    Args:
        entities (List[Dict[str, Any]]): List of raw entity dictionaries.
        output_path (Path): Path where the JSON file will be written.
        
    Returns:
        int: The number of successfully serialized entities.
    """
    sanitized_entities = []
    skipped_count = 0

    for idx, entity in enumerate(entities):
        # Defensive check: sanitize before adding to list
        safe_entity = sanitize_entity(entity)
        
        if safe_entity is not None:
            sanitized_entities.append(safe_entity)
        else:
            skipped_count += 1

    total_count = len(entities)
    
    # Log summary of the operation
    logger.info(
        f"Serialization complete. Total processed: {total_count}, "
        f"Skipped (invalid): {skipped_count}, "
        f"Written: {len(sanitized_entities)}."
    )

    if sanitized_entities:
        try:
            # Use indent for readability, sort_keys ensures consistent output order
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