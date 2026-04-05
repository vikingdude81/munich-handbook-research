from pydantic import BaseModel
from typing import List

class SpiritModel(BaseModel):
    name: str
    provenance: str
    verification: bool = False

# Example spirits (replace with actual data)
spirits = [
    SpiritModel(name="Spirit A", provenance="CLM 849, Iteration 1"),
    SpiritModel(name="Spirit B", provenance="CLM 849, Iteration 2"),
    # Add more spirits as needed
]

# Docstring
"""
This model represents spirits aggregated from CLM 849 and distilled during the distillation iteration.
Each spirit includes a name and provenance, with verification flags indicating validation status.
"""