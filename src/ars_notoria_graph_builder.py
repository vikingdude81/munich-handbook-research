from typing import Dict, List, Any

def build_ars_notoria_graph() -> Dict[str, Any]:
    """
    Constructs a minimal dict-based knowledge graph for the 'Ars Notoria' ritual.
    
    Returns:
        A dictionary containing 'nodes' and 'edges' lists representing the graph.
    """
    
    # Define stable, resolvable URIs as requested (e.g., munich:prefix)
    NODE_IDS = {
        "ritual": "munich:ars_notoria_ritual",
        "solomon": "munich:solomon",
        "holy_angels": "munich:holy_angels",
        "general_abilities": "munich:general_abilities",
        "prayer_beginning": "munich:prayer_beginning"
    }

    # Construct Nodes based on source material
    nodes: List[Dict[str, Any]] = [
        {
            "id": NODE_IDS["ritual"],
            "type": "ars_notoria",
            "name": "Ars Notoria",
            "description": "Angelic art of knowledge acquisition through prayer and notation",
            "also_known_as": "The Notory Art of Solomon"
        },
        {
            "id": NODE_IDS["solomon"],
            "type": "person",
            "name": "Solomon",
            "role": "recipient of revelation",
            "status": "biblical king and magician",
            "authorship": "Lemegeton, Treatise on Spiritual and Secret Experiments"
        },
        {
            "id": NODE_IDS["holy_angels"],
            "type": "spirit",
            "name": "Holy Angels",
            "role": "ministers of revelation",
            "function": "delivered knowledge upon altar of Temple"
        },
        {
            "id": NODE_IDS["general_abilities"],
            "type": "concept",
            "name": "General Abilities",
            "examples": ["memory", "eloquence", "understanding", "perseverance"]
        },
        {
            "id": NODE_IDS["prayer_beginning"],
            "type": "prayer",
            "name": "Prayer in the Beginning",
            "function": "Trinitarian invocation for illumination and knowledge",
            "status": "required preliminary"
        }
    ]

    # Construct Edges based on requested relations
    edges: List[Dict[str, str]] = [
        {
            "from": NODE_IDS["solomon"],
            "to": NODE_IDS["holy_angels"],
            "relation": "received_revelation_from"
        },
        {
            "from": NODE_IDS["ritual"],
            "to": NODE_IDS["general_abilities"],
            "relation": "has_purpose"
        },
        {
            "from": NODE_IDS["ritual"],
            "to": NODE_IDS["prayer_beginning"],
            "relation": "contains_prayer"
        },
        {
            "from": NODE_IDS["prayer_beginning"],
            "to": NODE_IDS["solomon"],
            "relation": "invoked_by"
        }
    ]

    # Assemble the final graph structure
    graph = {
        "nodes": nodes,
        "edges": edges
    }

    return graph

# Execution to demonstrate output
if __name__ == "__main__":
    graph_data = build_ars_notoria_graph()
    
    import json
    print(json.dumps(graph_data, indent=2))
