import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Define the canonical schema structure for entity storage
class EntityMetadata:
    def __init__(self, total: int, chunks: int, version: str):
        self.total_entities = total
        self.source_chunks = chunks
        self.extraction_version = version
        self.generated_at = datetime.utcnow().isoformat() + "Z"

class CanonicalEntity:
    def __init__(self, entity_type: str, content: str, attributes: Dict[str, Any], 
                 source_chunks: List[int], page_refs: List[str]):
        self.id = str(uuid.uuid4())
        self.type = entity_type
        self.content = content
        self.attributes = attributes
        self.source_chunks = source_chunks
        self.page_references = page_refs

class EntityWriter:
    """Handles atomic writeback of extracted entities to canonical JSON."""
    
    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.temp_path = self.output_path.with_suffix('.tmp')
        
    def validate_schema(self, data: Dict[str, Any]) -> bool:
        """Ensure the data conforms to expected structure before write."""
        required_keys = {'metadata', 'entities'}
        if not all(key in data for key in required_keys):
            raise ValueError("Missing required top-level keys: metadata or entities")
        
        if not isinstance(data['entities'], list):
            raise TypeError("'entities' must be a list of dictionaries")
            
        return True

    def write_atomic(self, entities_data: Dict[str, Any]) -> None:
        """Writes data to disk using atomic rename to prevent corruption on crash."""
        try:
            # Validate structure first
            self.validate_schema(entities_data)
            
            # Write to temporary file first
            with open(self.temp_path, 'w', encoding='utf-8') as f:
                json.dump(entities_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename (safer than overwrite on active filesystems)
            self.temp_path.rename(self.output_path)
            logger.info(f"Successfully wrote {len(entities_data['entities'])} entities to {self.output_path}")
        except Exception as e:
            logger.error(f"Writeback failed: {e}")
            if self.temp_path.exists():
                self.temp_path.unlink()
            raise

logger = logging.getLogger(__name__)
