from typing import Dict, List, Optional, Any, TypedDict
from enum import Enum

# =============================================================================
# SCHEMA DEFINITION: Ars Notoria Knowledge Graph
# =============================================================================
# This schema defines the structure for nodes and edges compatible with JSON-LD.
# It uses TypedDict for strict type checking and includes validation hints 
# (comments) mimicking Pydantic Field configurations.

class NodeProperty(TypedDict, total=False):
    """Base properties common to most nodes."""
    name: str  # Required: Unique identifier or display name
    description: str  # Optional: Human-readable description
    source_pages: List[int]  # Required: Page references from source material (e.g., [1, 7])

class RitualNode(TypedDict):
    """Represents a ritual or magical operation."""
    name: str
    description: str
    function: str  # Purpose of the ritual
    status: str  # e.g., 'active', 'forbidden', 'historical'
    source_pages: List[int]

class PrayerNode(TypedDict):
    """Represents a specific prayer or oration."""
    name: str
    function: str
    language_origin: str  # e.g., 'Chaldee', 'Greek', 'Hebrew'
    text_snippet: Optional[str]  # Validation Hint: max_length=500
    source_pages: List[int]

class DivineNameNode(TypedDict):
    """Represents a specific divine name or invocation."""
    name: str
    language_origin: str
    function: str
    part_of: str  # Reference to the prayer it belongs to
    source_pages: List[int]

class PersonNode(TypedDict):
    """Represents historical figures involved in the transmission."""
    name: str
    role: str  # e.g., 'recipient', 'translator', 'scholar'
    status: str  # e.g., 'biblical king', 'magician'
    date: Optional[str]  # Validation Hint: format='YYYY' or 'YYYY-MM-DD'
    source_pages: List[int]

class SpiritNode(TypedDict):
    """Represents angels, spirits, or divine entities."""
    name: str
    role: str
    function: str
    associated_days: Optional[List[int]]  # e.g., [4, 8, 12] for lunar days
    source_pages: List[int]

class ConceptNode(TypedDict):
    """Represents abstract concepts or abilities."""
    name: str
    category: str  # e.g., 'General Abilities', 'Liberal Arts'
    examples: Optional[List[str]]  # Validation Hint: min_length=1
    source_pages: List[int]

class RitualElementNode(TypedDict):
    """Represents components of the ritual."""
    name: str
    status: str
    pronunciation_timing: str  # e.g., 'fourth day of Moon'
    source_pages: List[int]

# =============================================================================
# EDGE DEFINITIONS
# =============================================================================
class EdgeProperty(TypedDict, total=False):
    """Base properties for relationships."""
    context: str  # Required: Contextual description of the link
    manuscript_variant: Optional[str]  # Validation Hint: regex='^MS_[A-Z0-9]+$'

class ReceivedRevelationFrom(EdgeProperty):
    """Spirit/Person -> Ritual"""
    context: str
    spirit_name: str  # Validation Hint: required=True

class UsedForAcquiring(EdgeProperty):
    """Ritual/Prayer -> Concept"""
    context: str
    ability_type: str  # e.g., 'memory', 'eloquence'

class RequiresFasting(EdgeProperty):
    """Operator -> Ritual"""
    context: str
    duration_days: int  # Validation Hint: min_length=1

class PartOf(EdgeProperty):
    """Component -> Whole (Prayer/DivineName)"""
    context: str
    parent_type: str  # e.g., 'prayer', 'ritual'

class Invokes(EdgeProperty):
    """Ritual/Prayer -> Spirit/DivineName"""
    context: str
    entity_name: str

class AttributedTo(EdgeProperty):
    """Work -> Person"""
    context: str
    author_role: str  # e.g., 'translator', 'author'

class MentionedIn(EdgeProperty):
    """Entity -> Source Page/Manuscript"""
    context: str
    manuscript_variant: Optional[str]
