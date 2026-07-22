"""
Entity Loader Module (munich_handbook_research)

This module provides a robust loader for entity data within the Munich Handbook research project.
It specifically addresses FileNotFoundError resilience by implementing a graceful degradation strategy:
1. Prioritizes 'munich_entities.json'.
2. Scans for alternative JSON files if primary is missing.
3. Generates a minimal placeholder schema if no valid file exists to ensure pipeline continuity.

Author: Expert Coder
Date: 2023-10-27
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logger to INFO level. 
# WARNING and ERROR levels are reserved for actual failures (e.g., corruption, permission denied).
# This prevents "FileNotFoundError" from being misinterpreted as a critical error in monitoring pipelines.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class EntityLoader:
    """
    Handles loading and initialization of entity data from JSON files.
    Implements recovery logic for missing or corrupted files.
    """

    # Schema keys required for a valid entity file
    REQUIRED_KEYS = ["entities", "source_chunks", "extraction_status"]
    
    # Placeholder schema for recovery state
    PLACEHOLDER_SCHEMA: Dict[str, Any] = {
        "entities": [],
        "source_chunks": 0,
        "extraction_status": "incomplete"
    }

    def __init__(self, base_directory: Path):
        """
        Initialize the loader with a target directory path.

        Args:
            base_directory (Path): The root directory to scan for entity files.
        """
        self.base_directory = base_directory.resolve()
        self.primary_file_path = self.base_directory / "munich_entities.json"
        self._data: Optional[Dict[str, Any]] = None

    def _ensure_directory_exists(self) -> None:
        """Ensures the target directory exists, creating it if necessary."""
        if not self.base_directory.exists():
            try:
                self.base_directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created base directory: {self.base_directory}")
            except OSError as e:
                # Log as error only for permission issues or disk full, etc.
                logger.error(f"Failed to create directory {self.base_directory}: {e}")
                raise

    def _find_alternative_json_files(self) -> List[Path]:
        """
        Scans the base directory for any existing .json files if primary is missing.
        
        Returns:
            List of Path objects representing found JSON files.
        """
        if self.primary_file_path.exists():
            return []

        json_files = list(self.base_directory.glob("*.json"))
        logger.info(f"Primary file 'munich_entities.json' not found. Scanned for alternatives.")
        return json_files

    def _validate_json_structure(self, data: Dict[str, Any]) -> bool:
        """
        Validates that the loaded JSON contains the required schema keys.

        Args:
            data (Dict): The parsed JSON content.

        Returns:
            bool: True if structure is valid, False otherwise.
        """
        missing_keys = [key for key in self.REQUIRED_KEYS if key not in data]
        
        if missing_keys:
            logger.warning(f"JSON structure incomplete. Missing keys: {missing_keys}")
            return False
        
        # Check if extraction_status allows loading (optional validation)
        status = data.get("extraction_status", "unknown")
        if status == "incomplete":
            logger.info("File marked as 'incomplete'. Proceeding with recovery logic.")
        
        return True

    def load_or_initialize(self) -> Dict[str, Any]:
        """
        Main entry point. Attempts to load entities or initialize a placeholder schema.
        
        Returns:
            Dict: The loaded entity data or placeholder schema.
        """
        self._ensure_directory_exists()
        
        # Try primary file first
        if self.primary_file_path.exists():
            try:
                with open(self.primary_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if self._validate_json_structure(data):
                    logger.info(f"Successfully loaded entities from {self.primary_file_path}")
                    self._data = data
                    return data
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load primary file: {e}. Attempting recovery.")
        
        # Try alternative JSON files
        alternatives = self._find_alternative_json_files()
        if alternatives:
            for alt_path in alternatives:
                try:
                    with open(alt_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if self._validate_json_structure(data):
                        logger.info(f"Loaded entities from alternative: {alt_path}")
                        self._data = data
                        return data
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Failed to load alternative {alt_path}: {e}")
            
            logger.warning("No valid alternative JSON files found.")
        
        # Return placeholder schema
        logger.info("No valid entity data found. Returning placeholder schema.")
        self._data = self.PLACEHOLDER_SCHEMA.copy()
        return self._data

    @property
    def data(self) -> Dict[str, Any]:
        """
        Property to access the loaded data.
        
        Returns:
            Dict: The current entity data.
        """
        if self._data is None:
            return self.load_or_initialize()
        return self._data

    def save(self, filepath: Optional[Path] = None) -> None:
        """
        Saves the current data to a JSON file.
        
        Args:
            filepath (Path): Optional path to save to. Defaults to primary_file_path.
        """
        if filepath is None:
            filepath = self.primary_file_path
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._data or self.PLACEHOLDER_SCHEMA, f, indent=2)
            logger.info(f"Saved entities to {filepath}")
        except IOError as e:
            logger.error(f"Failed to save entities: {e}")
            raise


if __name__ == "__main__":
    import sys
    
    # Default to current directory if no argument provided
    base_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    
    loader = EntityLoader(base_dir)
    entities = loader.load_or_initialize()
    
    print(f"Loaded {len(entities.get('entities', []))} entities")
    print(f"Source chunks: {entities.get('source_chunks', 0)}")
    print(f"Extraction status: {entities.get('extraction_status', 'unknown')}")