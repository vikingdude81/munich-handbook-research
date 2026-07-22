import os
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

# Configure logger once at module level if not already done
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        self.entities: List[Dict[str, Any]] = []
    
    def _resolve_project_root(self) -> Path:
        """Resolve the project root directory relative to this script."""
        # Move up two levels from src/loader.py (assuming structure: root/src/loader.py)
        return Path(__file__).parent.parent

    def load_entities(self, filename: str = "munich_entities.json") -> List[Dict[str, Any]]:
        """
        Attempts to load entity data with multiple fallback paths.
        Returns empty list if file is not found to prevent application crash.
        """
        project_root = self._resolve_project_root()
        
        # Fallback chain for path resolution
        candidates = [
            project_root / "data" / filename,  # Standard location
            project_root / filename,            # Root level
            Path.cwd() / filename              # Current working directory
        ]

        loaded_path: Optional[Path] = None
        
        for candidate in candidates:
            if candidate.exists():
                logger.info(f"Found {filename} at: {candidate}")
                try:
                    with open(candidate, 'r', encoding='utf-8') as f:
                        self.entities = json.load(f)
                    return self.entities
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in {candidate}: {e}")
                    continue
        
        # Graceful degradation if file not found
        logger.warning(f"Primary file '{filename}' not found. Scanned for alternatives.")
        logger.warning("Using empty entity list. Data extraction may be incomplete.")
        return self.entities