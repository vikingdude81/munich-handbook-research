import json
import os

# Define the directory path as requested
OUTPUT_DIR = r"E:\munich_handbook_research\data"

# Ensure the directory exists (simulated for this environment, but production-ready)
try:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
except OSError:
    # Fallback to local directory if E: drive is not available in current execution context
    OUTPUT_DIR = "./data"
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_knowledge_graph():
    """
    Builds a minimal knowledge graph schema and populates it with 
    extracted entities from the Ars Notoria source material.
    """

    # 1. Define Schema (JSON format)
    # This represents the structural requirements for each node type.
    schema = {
        "node_types": {
            "Prayer": {
                "required_fields": ["name", "function", "language_origin"]
            },
            "DivineName": {
                "required_fields": ["name", "function", "context"]
            },
            "Angel": {
                "required_flags": ["name", "role", "associated_days"]
            },
            "RitualDay": {
                "required_fields": ["description", "lunar_phase"]
            },
            "Language": {
                "required_fields": ["name", "origin_type"]
            },
            "LiberalArt": {
                "required_fields": ["name", "category"]
            }
        }
    }

    # 2. Extract and Populate Sample Nodes (Turtle/RDF format)
    # Using Turtle syntax for the graph representation as requested (.ttl)
    sample_nodes_ttl = """
@prefix ars: <http://example.org/ars_notoria/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Node 1: The Queen of Tongues Prayer
ars:QueenOfTongues 
    rdf:type ars:Prayer ;
    ars:name "The Queen of Tongues" ;
    ars:function "removes impediments of the tongue and grants eloquence" ;
    ars:language_origin "Chaldean Language" .

# Node 2: The Divine Name (Lameth...)
ars:DivineName_Lameth 
    rdf:type ars:DivineName ;
    ars:name "Lameth, Leynach, Semach, Belmay, Azzailement, Gesegon, Lothamasim, Ozetogomaglial, Zeziphier, Josanum, Solatac, Bozefama, Defarciamar, Zemait, Lemaio, Pheralon, Anuc, Philosophi, Gregoon, Letos, Anum" ;
    ars:function "invokes angels and provokes eloquence" ;
    ars:usage_context "to be said at beginning of month and Scripture" .

# Node 3: The Four Angels
ars:FourAngels 
    rdf:type ars:Angel ;
    ars:name "Four Angels" ;
    ars:role "revealers of orations" ;
    ars:associated_days "fourth day of the Moon" .
"""

    # Define file paths
    schema_path = os.path.join(OUTPUT_DIR, "graph_schema.json")
    nodes_path = os.path.join(OUTPUT_DIR, "sample_nodes.ttl")

    # Write Schema to JSON
    with open(schema_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=4)

    # Write Nodes to TTL
    with open(nodes_path, 'w', encoding='utf-8') as f:
        f.write(sample_nodes_ttl.strip())

    print(f"Success: Knowledge graph assets created in {OUTPUT_DIR}")
    print(f"Files generated: {os.path.basename(schema_path)}, {os.path.basename(nodes_path)}")


if __name__ == "__main__":
    create_knowledge_graph()
