"""
Entity Resolution Module for Ars Notoria Research Data.

This module processes raw text chunks from historical manuscripts to resolve 
ambiguous entities into a canonical JSON map. It applies bibliographic reasoning 
to distinguish between Persons, Spirits, and Ritual Tokens (divine names).

Author: Expert Coder
Date: 2023-10-27
"""

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class AuthorityRef:
    """Represents a bibliographic authority reference."""
    source: str  # e.g., "VIAF", "LOC", "RDA"
    identifier: str

    def to_dict(self) -> Dict[str, str]:
        return {"source": self.source, "identifier": self.identifier}


@dataclass
class ResolvedEntity:
    """Represents a resolved entity from the source material."""
    entity_id: str
    canonical_label: str
    type: str  # 'person', 'spirit', 'ritual_token', 'concept'
    authority_refs: List[AuthorityRef] = field(default_factory=list)
    manuscript_occurrences: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "canonical_label": self.canonical_label,
            "type": self.type,
            "authority_refs": [ref.to_dict() for ref in self.authority_refs],
            "manuscript_occurrences": self.manuscript_occurrences
        }


class EntityResolver:
    """
    Handles the resolution of entities based on source text and bibliographic rules.
    
    Logic:
    1. Parse raw chunks for entity mentions.
    2. Apply ground truth rules (e.g., Divine Names -> Ritual Token).
    3. Assign authority references where known.
    """

    # Ground Truth Rules based on Task Instructions
    GROUND_TRUTH_RULES = {
        "Solomon": {"type": "person", "authority": "VIAF:1096845"}, # King Solomon
        "Robert Turner": {"type": "person", "authority": "LOC (Catalog Entry)"}, # Translator 1657
        "Benjamin Rowe": {"type": "person", "authority": "Modern Scholar"}, # Editor 1999
    }

    def __init__(self, source_chunks: List[str]):
        self.source_chunks = source_chunks
        self.entities: Dict[str, ResolvedEntity] = {}

    def _count_occurrences(self, entity_id: str) -> int:
        """Count how many times an entity appears in the raw text chunks."""
        count = 0
        pattern = re.compile(re.escape(entity_id), re.IGNORECASE)
        for chunk in self.source_chunks:
            matches = pattern.findall(chunk)
            count += len(matches)
        return count

    def _resolve_authority(self, label: str) -> List[AuthorityRef]:
        """Determine authority references based on ground truth and logic."""
        refs = []
        
        # Check Ground Truth Rules
        if label in self.GROUND_TRUTH_RULES:
            rule = self.GROUND_TRUTH_RULES[label]
            ref = AuthorityRef(
                source=rule["authority"].split(":")[0], 
                identifier=rule["authority"].split(":")[1].strip()
            )
            refs.append(ref)
        else:
            # Default logic for unknowns (e.g., Ritual Tokens have no authority)
            if "ritual" in label.lower() or "divine_name" in label.lower():
                pass # No authority for ritual tokens
            elif "person" in label.lower():
                refs.append(AuthorityRef(source="LOC", identifier="Unknown/Modern"))

        return refs

    def resolve(self) -> List[Dict[str, Any]]:
        """Main resolution logic."""
        
        # 1. Extract potential entities from source text metadata tags
        # We look for patterns like [ars_notoria] person: Name or [ars_notoria] divine_name: Name
        raw_entities = []
        
        for chunk in self.source_chunks:
            # Regex to capture entity definitions within the provided format
            # Matches lines starting with [tag] type: label
            pattern = r'\[.*?\]\s+(person|divine_name|spirit|concept)\s*:\s*(.+?)\s*$'
            matches = re.findall(pattern, chunk)
            
            for match in matches:
                tag_type, label = match
                entity_id = f"{tag_type}:{label.lower().strip()}"
                raw_entities.append((entity_id, tag_type, label.strip()))
        
        # 2. Deduplicate and resolve entities
        for entity_id, tag_type, label in raw_entities:
            if entity_id not in self.entities:
                authority_refs = self._resolve_authority(label)
                occurrences = self._count_occurrences(label)
                
                entity = ResolvedEntity(
                    entity_id=entity_id,
                    canonical_label=label,
                    type=tag_type,
                    authority_refs=authority_refs,
                    manuscript_occurrences=occurrences
                )
                self.entities[entity_id] = entity
        
        # 3. Return resolved entities as dictionaries
        return [e.to_dict() for e in self.entities.values()]


def process_source_chunks(chunks: List[str]) -> Dict[str, Any]:
    """
    Main entry point for processing source chunks.
    
    Args:
        chunks: List of raw text chunks from manuscripts
    
    Returns:
        Dictionary containing resolved entities and statistics
    """
    resolver = EntityResolver(chunks)
    results = resolver.resolve()
    
    return {
        "total_entities": len(results),
        "entities_by_type": {},
        "results": results
    }


if __name__ == "__main__":
    # Example usage with mock data
    mock_chunks = [
        "[ars_notoria] person: Solomon",
        "[ars_notoria] divine_name: YHWH",
        "[ars_notoria] concept: Ars Notoria",
        "Solomon is mentioned in the text multiple times."
    ]
    
    result = process_source_chunks(mock_chunks)
    print(json.dumps(result, indent=2))