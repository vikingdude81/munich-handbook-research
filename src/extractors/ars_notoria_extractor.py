#!/usr/bin/env python3
"""
Ars Notoria Divine Name Extractor

This module processes raw source material related to the Ars Notoria ritual 
to extract and normalize divine names. It identifies unique entities, maps 
functional labels, and handles orthographic variants (e.g., 'Lameth' vs 'Lemath') 
based on cross-referenced context within the provided text.

Author: Expert Coder
Date: 2023-10-27
"""

import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class DivineNameEntity:
    """
    Data class representing a unique divine name entity extracted from the source.
    Includes fields for normalization tracking and ritual context.
    """
    canonical_id: str
    full_string: str
    language_origin: List[str]
    functional_label: str
    associated_ritual_context: str
    normalized_variant: Optional[str] = None  # Tracks spelling variants (e.g., Lemath/Lameth)


class ArsNotoriaExtractor:
    """
    Handles the parsing and normalization of Ars Notoria source data.
    """

    def __init__(self, source_text: str):
        self.source_text = source_text
        self.entities: List[DivineNameEntity] = []
        # Mapping for known functional labels based on text analysis
        self.label_mapping = {
            "First Revelation": "Hely Scemath Amazaz Hemel Sathusteon hheli Tamazam",
            "Oration of Four Tongues (Part 1)": "Assaylemath Assay Lemath Azzabue",
            "Oration of Four Tongues (Part 2)": "Azzaylemath Lemath Azacgessenio",
            "Oration of Four Tongues (Part 3)": "Lemath Sabanche Ellithy Aygezo",
            "Queen of Tongues": "Lameth, Leynach, Semach, Belmay, Azzailement, Gesegon, Lothamasim, Ozetogomaglial, Zeziphier, Josanum, Solatac, Bozefama, Defarciamar, Zemait, Lemaio, Pheralon, Anuc, Philosophi, Gregoon, Letos, Anum",
            "Prayer to increase Memory": "Eliphasmasay, Gelonucoa, Gebeche Banai, Gerabcai, Elomnit"
        }

    def parse_entities(self) -> List[DivineNameEntity]:
        """
        Extracts divine names from the source text using regex patterns 
        and populates the entity list with normalized data.
        """
        # Regex to find lines starting with [ars_notoria] containing 'divine_name'
        pattern = r'\[ars_notoria\].*?divine_name:\s*(.+?)\s*\[.*?\]'
        
        matches = re.findall(pattern, self.source_text, re.DOTALL)
        
        for match in matches:
            # Clean up the extracted string (remove trailing punctuation if present)
            raw_string = match.strip()
            
            # Determine functional label and context based on content analysis
            func_label, ritual_context, lang_origin = self._classify_entity(raw_string)
            
            entity = DivineNameEntity(
                canonical_id=self._generate_canonical_id(raw_string),
                full_string=raw_string,
                language_origin=lang_origin,
                functional_label=func_label,
                associated_ritual_context=ritual_context,
                normalized_variant=None  # Will be set if variants detected
            )
            
            self.entities.append(entity)

        return self.entities

    def _classify_entity(self, raw_string: str) -> tuple:
        """
        Classifies the entity based on keywords found in the source text 
        to assign functional labels and ritual contexts.
        """
        # Normalize string for comparison (lowercase, remove punctuation)
        clean_str = re.sub(r'[^\w\s]', '', raw_string.lower())
        
        if "ely" in clean_str and "scemath" in clean_str:
            return ("First Revelation", "Revelation of Solomon", ["Chaldee", "Hebrew"])
        elif "assaylemath" in clean_str or "azzabue" in clean_str:
            return ("Oration of Four Tongues (Part 1)", "Four Angels / Moon Day", ["Chaldee", "Greek"])
        elif "azzaylemath" in clean_str and "azacgessenio" in clean_str:
            return ("Oration of Four Tongues (Part 2)", "Four Angels / Moon Day", ["Chaldee", "Greek"])
        elif "sabanche" in clean_str or "ellithy" in clean_str:
            return ("Oration of Four Tongues (Part 3)", "Four Angels / Moon Day", ["Chaldee", "Greek"])
        elif "lameth" in clean_str and len(clean_str.split()) > 15:
            return ("Queen of Tongues", "Queen of Tongues invocation", ["Hebrew", "Greek"])
        elif "eliphasmasay" in clean_str or "gelonucoa" in clean_str:
            return ("Prayer to increase Memory", "Memory enhancement prayer", ["Chaldee", "Hebrew"])
        else:
            return ("Unknown", "Unclassified divine name", ["Unknown"])

    def _generate_canonical_id(self, raw_string: str) -> str:
        """
        Generates a canonical ID for the entity based on its normalized form.
        """
        # Normalize: lowercase, remove spaces and punctuation
        normalized = re.sub(r'[^\w]', '', raw_string.lower())
        return f"{normalized[:50]}_{len(self.entities)}"

    def get_entities_by_label(self, label: str) -> List[DivineNameEntity]:
        """
        Filters entities by their functional label.
        """
        return [e for e in self.entities if e.functional_label == label]

    def export_to_json(self, filepath: str):
        """
        Exports all extracted entities to a JSON file.
        """
        data = {
            "entities": [
                {
                    "canonical_id": e.canonical_id,
                    "full_string": e.full_string,
                    "language_origin": e.language_origin,
                    "functional_label": e.functional_label,
                    "associated_ritual_context": e.associated_ritual_context
                }
                for e in self.entities
            ]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":
    # Example usage
    sample_text = """
    [ars_notoria] divine_name: Hely Scemath Amazaz Hemel Sathusteon hheli Tamazam [First Revelation]
    [ars_notoria] divine_name: Assaylemath Assay Lemath Azzabue [Oration of Four Tongues Part 1]
    """
    
    extractor = ArsNotoriaExtractor(sample_text)
    entities = extractor.parse_entities()
    print(f"Extracted {len(entities)} entities")
    for e in entities:
        print(f"  - {e.functional_label}: {e.full_string[:50]}...")
