"""
Symbolic Correspondence Engine (Agrippa-based)

Implements a typed domain model for inferential demonology based on 
Agrippa's *De occulta philosophia* Book III schema. Supports planetary 
rulerships, elemental affinities, and temporal window matching.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
import re
from datetime import datetime


# =============================================================================
# ENUMERATIONS
# =============================================================================

class Planet(Enum):
    """Classical planetary rulers from Agrippa's schema."""
    SATURN = "saturn"
    JUPITER = "jupiter"
    MARS = "mars"
    SUN = "sun"
    MOON = "moon"
    MERCURY = "mercury"
    VENUS = "venus"


class Element(Enum):
    """Classical elements with Agrippa correspondences."""
    FIRE = "fire"
    AIR = "air"
    WATER = "water"
    EARTH = "earth"


# =============================================================================
# DOMAIN MODELS
# =============================================================================

@dataclass(frozen=True)
class Demon:
    """
    Agrippa-style demon entity with symbolic correspondences.
    
    Attributes:
        name: Demon's proper name (Latin or vernacular)
        planetary_ruler: Planet governing this demon
        elemental_affinity: Primary elemental correspondence
        temporal_window: Tuple of (day_index, hour_index) for invocation
        required_materials: List of ritual materials for summoning
    """
    name: str
    planetary_ruler: Planet
    elemental_affinity: Literal['fire', 'air', 'water', 'earth']
    temporal_window: Tuple[int, int]  # (day_of_week, hour_of_day)
    required_materials: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate elemental affinity is valid."""
        if self.elemental_affinity not in Element.__members__:
            raise ValueError(f"Invalid element: {self.elemental_affinity}")
    
    @property
    def day_name(self) -> str:
        """Return human-readable day name from index."""
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", 
                "Thursday", "Friday", "Saturday"]
        return days[self.temporal_window[0]]
    
    @property
    def hour_description(self) -> str:
        """Return human-readable hour description."""
        hours = [f"{h}th hour" for h in range(1, 25)]
        return hours[self.temporal_window[1] - 1] if self.temporal_window[1] > 0 else "Nocturnal"


# =============================================================================
# CORRESPONDENCE MAPPINGS
# =============================================================================

class CorrespondenceTable:
    """
    Static mapping tables for symbolic inference.
    
    Encapsulates Agrippa's planetary, elemental, and material 
    correspondences used during context analysis.
    """
    
    # Planetary keyword mappings (material → planet)
    MATERIAL_TO_PLANET: Dict[str, Planet] = {
        "iron": Planet.MARS,
        "steel": Planet.MARS,
        "red": Planet.MARS,
        "blood": Planet.MARS,
        "gold": Planet.JUPITER,
        "yellow": Planet.JUPITER,
        "silver": Planet.MERCURY,
        "white": Planet.MERCURY,
        "copper": Planet.VENUS,
        "green": Planet.VENUS,
        "lead": Planet.SATURN,
        "black": Planet.SATURN,
        "tin": Planet.MOON,
        "blue": Planet.MOON,
    }
    
    # Color-to-element mappings
    COLOR_TO_ELEMENT: Dict[str, Element] = {
        "red": Element.FIRE,
        "orange": Element.FIRE,
        "yellow": Element.FIRE,
        "green": Element.AIR,
        "blue": Element.WATER,
        "brown": Element.EARTH,
    }


class TemporalWindow:
    """
    Handles temporal calculations for ritual windows.
    
    Based on the 24-hour astrological day system where each hour
    is ruled by a planet in sequence starting from sunrise.
    """
    
    PLANETARY_HOURS = [Planet.MOON, Planet.MERCURY, Planet.VENUS,
                       Planet.SUN, Planet.MARS, Planet.JUPITER, Planet.SATURN]
    
    @classmethod
    def get_planetary_hour(cls, hour_index: int) -> Planet:
        """
        Get the planet ruling a specific hour.
        
        Args:
            hour_index: 0-23 for daytime hours (1-24 in traditional counting)
        
        Returns:
            The planetary ruler for this hour
        """
        return cls.PLANETARY_HOURS[hour_index % len(cls.PLANETARY_HOURS)]
    
    @classmethod
    def get_day_planet(cls, day_index: int) -> Planet:
        """
        Get the planet ruling a specific day.
        
        Args:
            day_index: 0-6 (Sunday=0)
        
        Returns:
            The planetary ruler for this day
        """
        days = [Planet.SUN, Planet.MOON, Planet.MARS, Planet.MERCURY,
                Planet.JUPITER, Planet.VENUS, Planet.SATURN]
        return days[day_index % len(days)]


# =============================================================================
# SYMBOLIC CORRESPONDENCE ENGINE
# =============================================================================

class SymbolicCorrespondenceEngine:
    """
    Main engine for symbolic inference and demon summoning.
    
    Analyzes input contexts against Agrippa's correspondences to
    identify appropriate demons, materials, and temporal windows.
    """
    
    # Sample demon database (expanding in production)
    DEMON_DATABASE: Dict[str, Demon] = {
        "Bael": Demon(
            name="Bael",
            planetary_ruler=Planet.MARS,
            elemental_affinity="fire",
            temporal_window=(2, 10),
            required_materials=["iron", "red cloth", "blood"]
        ),
        "Asmodeus": Demon(
            name="Asmodeus",
            planetary_ruler=Planet.MARS,
            elemental_affinity="fire",
            temporal_window=(2, 14),
            required_materials=["iron", "red wax", "incense"]
        ),
        "Lucifer": Demon(
            name="Lucifer",
            planetary_ruler=Planet.MERCURY,
            elemental_affinity="air",
            temporal_window=(3, 8),
            required_materials=["silver", "white cloth", "myrrh"]
        ),
        "Paimon": Demon(
            name="Paimon",
            planetary_ruler=Planet.JUPITER,
            elemental_affinity="air",
            temporal_window=(4, 12),
            required_materials=["gold", "yellow cloth", "frankincense"]
        ),
    }
    
    def __init__(self):
        """Initialize the correspondence engine."""
        self.correspondence_table = CorrespondenceTable()
        self.temporal_window = TemporalWindow()
    
    def analyze_material(self, material: str) -> Optional[Planet]:
        """
        Analyze a material to determine its planetary ruler.
        
        Args:
            material: Material name or color description
        
        Returns:
            The corresponding planet, or None if no match found
        """
        material_lower = material.lower().strip()
        return self.correspondence_table.MATERIAL_TO_PLANET.get(material_lower)
    
    def analyze_color(self, color: str) -> Optional[Element]:
        """
        Analyze a color to determine its elemental affinity.
        
        Args:
            color: Color name
        
        Returns:
            The corresponding element, or None if no match found
        """
        color_lower = color.lower().strip()
        return self.correspondence_table.COLOR_TO_ELEMENT.get(color_lower)
    
    def find_demon_by_material(self, material: str) -> Optional[Demon]:
        """
        Find demons associated with a given material.
        
        Args:
            material: Material to search for
        
        Returns:
            List of matching demons, or empty list if none found
        """
        planet = self.analyze_material(material)
        if not planet:
            return []
        
        return [d for d in self.DEMON_DATABASE.values() 
                if d.planetary_ruler == planet]
    
    def find_demon_by_element(self, element: Element) -> List[Demon]:
        """
        Find demons associated with a given element.
        
        Args:
            element: Elemental affinity to search for
        
        Returns:
            List of matching demons
        """
        return [d for d in self.DEMON_DATABASE.values() 
                if d.elemental_affinity == element.value]
    
    def get_optimal_invocation_time(self, demon: Demon) -> str:
        """
        Get the optimal invocation time for a demon.
        
        Args:
            demon: The demon to find timing for
        
        Returns:
            Human-readable description of optimal time
        """
        day_name = demon.day_name
        hour_desc = demon.hour_description
        return f"{day_name} at the {hour_desc}"
    
    def suggest_materials(self, elemental_affinity: Element) -> List[str]:
        """
        Suggest materials based on elemental affinity.
        
        Args:
            elemental_affinity: The element to base suggestions on
        
        Returns:
            List of suggested materials
        """
        materials = []
        for material, planet in self.correspondence_table.MATERIAL_TO_PLANET.items():
            if self.temporal_window.get_day_planet(self._get_day_index(material)) == planet:
                materials.append(material)
        return materials
    
    def _get_day_index(self, material: str) -> int:
        """Get day index from material's planetary correspondence."""
        planet = self.analyze_material(material)
        if not planet:
            return 0
        days = [Planet.SUN, Planet.MOON, Planet.MARS, Planet.MERCURY,
                Planet.JUPITER, Planet.VENUS, Planet.SATURN]
        return days.index(planet)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def parse_temporal_window(day_str: str, hour_str: str) -> Tuple[int, int]:
    """
    Parse temporal window from string inputs.
    
    Args:
        day_str: Day of week (e.g., "Tuesday")
        hour_str: Hour description (e.g., "10th hour")
    
    Returns:
        Tuple of (day_index, hour_index)
    """
    days = ["Sunday", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday"]
    day_index = days.index(day_str.lower()) if day_str.lower() in [d.lower() for d in days] else 0
    
    hour_match = re.search(r'(\d+)', hour_str)
    hour_index = int(hour_match.group(1)) if hour_match else 1
    
    return (day_index, hour_index)

def create_demon_from_context(context: str) -> Optional[Demon]:
    """
    Create a demon entity from contextual analysis.
    
    This is a placeholder for future LLM-based context analysis.
    
    Args:
        context: Contextual description or query
    
    Returns:
        Demon instance if matched, None otherwise
    """
    # TODO: Implement LLM-based context analysis
    return None


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    engine = SymbolicCorrespondenceEngine()
    
    # Example usage
    print("Symbolic Correspondence Engine Initialized")
    print(f"Available demons: {list(engine.DEMON_DATABASE.keys())}")
    
    # Test material analysis
    planet = engine.analyze_material("iron")
    print(f"Iron corresponds to: {planet}")
    
    # Test demon lookup
    demons = engine.find_demon_by_material("iron")
    for d in demons:
        print(f"  - {d.name}: {d.elemental_affinity} ({d.day_name})")
    
    # Test temporal window
    demon = list(engine.DEMON_DATABASE.values())[0]
    print(f"Optimal invocation: {engine.get_optimal_invocation_time(demon)}")