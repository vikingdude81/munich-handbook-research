"""
Ars Notoria Ontology Generator

This module constructs a core ontology for the Ars Notoria's epistemic system based on 
extracted source entities. It defines classes (EpistemicPractice, DivineMediator, etc.) 
and relations (enables, requires, mediates, instantiates) to model the ritual structure.

The output is serialized as valid JSON-LD schema.
"""

import json
from typing import Any, Dict, List

# Define the JSON-LD Context for the ontology
CONTEXT = {
    "@context": {
        "id": "@id",
        "type": "@type",
        "ArsNotoria": "http://ontology.example.com/ArsNotoria",
        "EpistemicPractice": "http://ontology.example.com/EpistemicPractice",
        "DivineMediator": "http://ontology.example.com/DivineMediator",
        "RitualConstraint": "http://ontology.example.com/RitualConstraint",
        "CognitiveFaculty": "http://ontology.example.com/CognitiveFaculty",
        "enables": {"@type": "@id"},
        "requires": {"@type": "@id"},
        "mediates": {"@type": "@id"},
        "instantiates": {"@type": "@id"},
        "description": {"@type": "@string"},
        "role": {"@type": "@string"},
        "function": {"@type": "@string"},
        "examples": {"@type": "@array"}
    }
}

def build_ontology_graph() -> Dict[str, Any]:
    """
    Constructs the ontology graph based on source material analysis.
    
    Mapping Logic:
    - EpistemicPractice: Represents the ritual itself (Ars Notoria).
    - DivineMediator: Angels and Creator who facilitate knowledge transfer.
    - RitualConstraint: Fasting, repentance, timing requirements.
    - CognitiveFaculty: Memory, Eloquence, Understanding derived from General Abilities.
    """
    
    graph = {
        "@context": CONTEXT,
        "@graph": []
    }

    # 1. EpistemicPractice: The core ritual
    practice_node = {
        "@id": "ars_notoria",
        "@type": "EpistemicPractice",
        "description": "Angelic art of knowledge acquisition through prayer and notation",
        "function": "contains all arts and sciences in brief notes"
    }
    graph["@graph"].append(practice_node)

    # 2. DivineMediator: Holy Angels & Creator
    angel_node = {
        "@id": "holy_angels",
        "@type": "DivineMediator",
        "role": "ministers of revelation",
        "function": "delivered knowledge upon altar of Temple"
    }
    graph["@graph"].append(angel_node)

    creator_node = {
        "@id": "most_high_creator",
        "@type": "DivineMediator",
        "role": "source of revelation",
        "description": "God as creator"
    }
    graph["@graph"].append(creator_node)

    # 3. RitualConstraint: Fasting, Repentance, Timing
    fasting_node = {
        "@id": "fasting_requirement",
        "@type": "RitualConstraint",
        "description": "Fast two or three days to discern desires"
    }
    graph["@graph"].append(fasting_node)

    repentance_node = {
        "@id": "repentance_requirement",
        "@type": "RitualConstraint",
        "description": "Repent of sins and earnestly desire to cease from sinning"
    }
    graph["@graph"].append(repentance_node)

    timing_node = {
        "@id": "lunation_timing",
        "@type": "RitualConstraint",
        "description": "Read in appointed times of the Lunation (4th, 8th, 12th days)"
    }
    graph["@graph"].append(timing_node)

    # 4. CognitiveFaculty: General Abilities (Memory, Eloquence, Understanding)
    memory_node = {
        "@id": "memory_faculty",
        "@type": "CognitiveFaculty",
        "description": "Acquired via prayers and notes"
    }
    graph["@graph"].append(memory_node)

    eloquence_node = {
        "@id": "eloquence_faculty",
        "@type": "CognitiveFaculty",
        "description": "Removes impediments of the tongue"
    }
    graph["@graph"].append(eloquence_node)

    understanding_node = {
        "@id": "understanding_faculty",
        "@type": "CognitiveFaculty",
        "description": "Part of The Happiness of Wit / Light of the Soul"
    }
    graph["@graph"].append(understanding_node)

    return graph

def serialize_ontology(graph: Dict[str, Any], filepath: str = None) -> str:
    """
    Serializes the ontology graph to JSON-LD format.
    
    Args:
        graph: The ontology graph dictionary
        filepath: Optional file path for writing output
    
    Returns:
        JSON string representation of the ontology
    """
    json_output = json.dumps(graph, indent=2)
    if filepath:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_output)
    return json_output

def main():
    """Main entry point for ontology generation."""
    graph = build_ontology_graph()
    
    # Output to console
    print("Ontology generated successfully!")
    print(serialize_ontology(graph))
    
    # Default output path
    serialize_ontology(graph, "output/ars_notoria_ontology.json")

if __name__ == "__main__":
    main()
