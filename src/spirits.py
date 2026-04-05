from dataclasses import dataclass
from typing import List, Optional, Dict
import os

@dataclass
class Spirit:
    id: int
    name: str
    description: str
    created_at: Optional[str] = None

def load_distilled_spirts(directory: str) -> List[Spirit]:
    """
    Load distilled spirit models from the specified directory.

    Args:
        directory (str): Path to the directory containing distilled spirit files.

    Returns:
        List[Spirit]: A list of Spirit objects loaded from the directory.
    """
    if not os.path.exists(directory):
        return []

    spirits = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r') as f:
                data = f.read()
                # Parse JSON data into Spirit object
                # (Implementation details depend on file structure)
                spirits.append(Spirit(id=1, name='Sample', description='Description'))
    return spirits
