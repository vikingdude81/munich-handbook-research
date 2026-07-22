"""
Ars Notoria Divine Name Extraction Module.

This module encapsulates the extracted divine name invocations from the provided 
source material regarding the Ars Notoria. It defines a data structure representing 
the catalog of names, functions, contexts, and manuscript references found in the 
research phase data (E:\munich_handbook_research).

Note: This script hardcodes the extracted data based on the provided text snippet 
as external file system access is not available in this environment.
"""

import json
from typing import List, Dict


def get_ars_notoria_divine_names() -> List[Dict[str, str]]:
    """
    Returns a structured list of divine name invocations extracted from the 
    Ars Notoria source material.

    Fields:
        - name (str): The specific divine name or invocation string.
        - function (str): The purpose or effect of the invocation.
        - context (str): The ritual timing or condition for usage.
        - manuscript_reference (str): Page reference from the source text.
    """
    
    # Data extracted based on structured entity tags in the provided source snippet.
    # Specifically targeting 'divine_name' entities and associated metadata.
    divine_names_data: List[Dict[str, str]] = [
        {
            "name": "Hely Scemath Amazaz Hemel Sathusteon hheli Tamazam",
            "function": "First Revelation of Solomon; Science of transcendent purity",
            "context": "Without any Interpretation; read in appointed times of the Lunation",
            "manuscript_reference": "[p.13]"
        },
        {
            "name": "Assaylemath Assay Lemath Azzabue",
            "function": "Part of the Oration of the four Tongues",
            "context": "Pronounced at beginning of month and Scripture",
            "manuscript_reference": "[p.14]"
        },
        {
            "name": "Azzaylemath Lemath Azacgessenio",
            "function": "Second part of the precedent Oration",
            "context": "Pronounced at beginning of month and Scripture",
            "manuscript_reference": "[p.14]"
        },
        {
            "name": "Lemath Sabanche Ellithy Aygezo",
            "function": "Third part of the precedent Oration",
            "context": "Pronounced at beginning of month and Scripture",
            "manuscript_reference": "[p.14]"
        },
        {
            "name": "Lameth, Leynach, Semach, Belmay, Azzailement, Gesegon, Lothamasim, Ozetogomaglial, Zeziphier, Josanum, Solatac, Bozefama, Defarciamar, Zemait, Lemaio, Pheralon, Anuc, Philosophi, Gregoon, Letos, Anum",
            "function": "Invokes angels and provokes eloquence",
            "context": "To be said at beginning of month and Scripture",
            "manuscript_reference": "[p.17]"
        },
        {
            "name": "Eliphasmasay, Gelonucoa, Gebeche Banai, Gerabcai, Elomnit",
            "function": "Archangels invoked for memory",
            "context": "In prayer to increase Memory",
            "manuscript_reference": "[p.17]"
        }
    ]
    
    return divine_names_data


def export_to_json(data: List[Dict[str, str]], filename: str = None) -> str:
    """
    Serializes the extracted data into a JSON string.

    Args:
        data (List[Dict]): The list of dictionaries containing name data.
        filename (str, optional): If provided, writes to file instead of returning string.

    Returns:
        str: The serialized JSON string.
    """
    json_output = json.dumps(data, indent=4, ensure_ascii=False)
    
    if filename:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_output)
            
    return json_output


if __name__ == "__main__":
    # Retrieve the cataloged data
    names = get_ars_notoria_divine_names()
    
    # Generate and print the JSON output to stdout
    print(export_to_json(names))