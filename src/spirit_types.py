from typing import TypeVar, Generic, Optional, Dict, List
from typing_extensions import TypedDict

class Spirit(TypedDict):
    name: str
    date: int  # Assuming date is represented as an integer (e.g., Unix timestamp)
    ingredients: Dict[str, float]
    steps: List[str]

class Experiment(TypedDict):
    spirit_id: int
    description: Optional[str] = None
    results: Optional[Dict[str, str]] = None

def is_complete(spirit: Spirit) -> bool:
    return all([value != "" for value in spirit.values()])

def has_provenance(spirit: Spirit) -> bool:
    return "provenance" in spirit and isinstance(spirit["provenance"], list)

# Example usage
spirit1 = Spirit(name="Vodka", date=1609348800, ingredients={"water": 50.0, "grain alcohol": 50.0}, steps=["mix", "heat"])
print(is_complete(spirit1))  # True

experiment1 = Experiment(star_id=1, description="Test experiment")
print(has_provenance(experiment1))  # False