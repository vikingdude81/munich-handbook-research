import os
from pathlib import Path
import logging
from typing import Optional, Dict, Any

# Configure logging to capture actual paths and errors gracefully
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class ResearchDirectoryManager:
    """
    Manages file system checks for the research directory.
    Ensures robust path resolution and graceful error handling.
    """

    # Default target path as specified in requirements
    DEFAULT_PATH = r"E:\munich_handbook_research"

    def __init__(self, target_path: str = None):
        """
        Initialize the manager with a specific path or default.
        
        Args:
            target_path: The directory path to manage. Defaults to DEFAULT_PATH.
        """
        self._target_path = target_path or self.DEFAULT_PATH
        # Resolve to absolute path immediately for consistency
        self._resolved_path = os.path.abspath(self._target_path)

    @property
    def resolved_path(self) -> str:
        """Returns the absolute path string."""
        return self._resolved_path

    def pre_flight_check(self) -> Optional[Dict[str, Any]]:
        """
        Performs a pre-flight check on the directory.
        
        (a) Checks if directory exists. If found, lists contents. 
            If not found, logs the actual path and returns empty data.
        (b) Replaces strict FileNotFoundError with graceful fallbacks.
        (c) Logs the *actual* path being accessed when errors occur.
        
        Returns:
            Dict containing directory info if successful, None otherwise.
        """
        logger.info(f"Starting pre-flight check for resolved path: {self._resolved_path}")

        try:
            # Use Path object for robust iteration
            p = Path(self._resolved_path)
            
            # Check existence first to avoid unnecessary errors
            if not p.exists():
                # Log the actual path being accessed when error occurs (Requirement c)
                logger.warning(f"Directory does not exist at: {self._resolved_path}")
                
                # Graceful fallback: Return empty dict instead of raising (Requirement b)
                return {}

            # List directory contents if found (Requirement a logic correction: 
            # Listing non-existent paths is impossible, so we list only if exists)
            contents = []
            for item in p.iterdir():
                contents.append({
                    'name': item.name,
                    'is_dir': item.is_dir(),
                    'path': str(item.resolve())
                })

            return {
                'status': 'success',
                'path': self._resolved_path,
                'contents': contents,
                'total_items': len(contents)
            }

        except FileNotFoundError as e:
            # Requirement (b): Replace strict raises with graceful fallbacks
            logger.error(f"FileNotFoundError occurred for path: {self._resolved_path}. Error: {e}")
            return {}
        
        except PermissionError as e:
            # Additional robustness for permission issues
            logger.error(f"Permission denied accessing path: {self._resolved_path}. Error: {e}")
            return {}

        except Exception as e:
            # Catch-all for unexpected errors during resolution
            logger.exception(f"Unexpected error checking path: {self._resolved_path}")
            return {}


def main():
    """Entry point to demonstrate robust path handling."""
    manager = ResearchDirectoryManager()
    
    # Execute pre-flight check
    result = manager.pre_flight_check()
    
    if result and result.get('status') == 'success':
        print(f"Found {result['total_items']} items in: {result['path']}")
    else:
        print("Pre-flight check completed. No data returned.")


if __name__ == "__main__":
    main()
