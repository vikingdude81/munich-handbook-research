"""
Entity Disambiguation and Deduplication Module for Ars Notoria Dataset.

This module processes pre-distilled source data to identify, merge, and canonicalize
entities related to 'Solomon'. It handles role aggregation, attribute merging, 
and rationale generation for the deduplication process.
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class RawEntity:
    """Represents a raw entity entry from the source text."""
    type: str  # e.g., 'person', 'divine_name'
    name: str
    role: Optional[str] = None
    status: Optional[str] = None
    title: Optional[str] = None
    authorship: Optional[str] = None
    pages: List[str] = field(default_factory=list)


@dataclass
class CanonicalEntity:
    """Represents a deduplicated, canonical entity."""
    id: str
    name: str
    roles: List[str]
    attributes: Dict[str, Any]
    merge_rationale: str
    source_pages: List[str] = field(default_factory=list)


class EntityResolver:
    """
    Handles the resolution and deduplication of entities based on name matching 
    and attribute overlap.
    """

    def __init__(self):
        self.entities: Dict[str, CanonicalEntity] = {}

    def parse_raw_entry(self, line: str) -> Optional[RawEntity]:
        """Parses a raw string line into a structured RawEntity object."""
        # Expected format: [tag] person: Name (role=..., status=...) [pages]
        if not line.startswith("[ars_notoria]"):
            return None

        try:
            content = line.split("]", 1)[1].strip()
            parts = content.split(": ", 1)
            if len(parts) < 2:
                return None
            
            entity_type, details = parts
            name_match = details.split(" (", 1)
            
            if len(name_match) < 2:
                return None
                
            name = name_match[0].strip()
            meta = name_match[1]

            # Extract attributes from parentheses
            attrs = {}
            for attr in ["role=", "status=", "title=", "authorship="]:
                if attr in meta:
                    end_idx = meta.find(")", meta.index(attr))
                    value = meta[meta.index(attr) + len(attr):end_idx].strip()
                    attrs[attr] = value
            
            # Extract pages from brackets at the end
            page_start = meta.rfind("[")
            if page_start != -1:
                pages_str = meta[page_start:]
                pages = [p.strip().replace("]", "").replace("[", "") for p in pages_str.split(",")]

            return RawEntity(
                type=entity_type,
                name=name,
                role=attrs.get("role"),
                status=attrs.get("status"),
                title=attrs.get("title"),
                authorship=attrs.get("authorship"),
                pages=pages
            )
        except Exception:
            return None

    def resolve_solomon_entities(self, raw_entries: List[str]) -> CanonicalEntity:
        """
        Identifies all 'Solomon' related entries and merges them into a canonical form.
        """
        solomon_candidates = []

        for line in raw_entries:
            entity = self.parse_raw_entry(line)
            if entity and entity.name.lower() == "solomon":
                solomon_candidates.append(entity)

        if not solomon_candidates:
            raise ValueError("No Solomon entities found in input data.")

        # Merge Logic
        merged_roles = set()
        merged_status = ""
        merged_title = ""
        merged_authorship = []
        all_pages = set()

        for candidate in solomon_candidates:
            if candidate.role:
                # Normalize role strings (e.g., "recipient of revelation" -> "recipient")
                role_normalized = candidate.role.split(" ")[0]
                merged_roles.add(role_normalized)
            
            if candidate.status:
                merged_status = candidate.status
            
            if candidate.title:
                merged_title = candidate.title
            
            if candidate.authorship:
                merged_authorship.append(candidate.authorship)
            
            all_pages.update(candidate.pages)

        # Generate merge rationale
        rationale_parts = []
        if len(solomon_candidates) > 1:
            rationale_parts.append(f"Merged {len(solomon_candidates)} entries")
        else:
            rationale_parts.append("Single entry found")
        
        if merged_roles:
            rationale_parts.append(f"Roles: {', '.join(sorted(merged_roles))}")
        
        if all_pages:
            rationale_parts.append(f"Sources: {len(all_pages)} pages")

        return CanonicalEntity(
            id="solomon_canonical",
            name="Solomon",
            roles=list(merged_roles),
            attributes={
                "status": merged_status,
                "title": merged_title,
                "authorship": merged_authorship
            },
            merge_rationale="; ".join(rationale_parts),
            source_pages=list(all_pages)
        )

    def resolve_all_entities(self, raw_entries: List[str]) -> Dict[str, CanonicalEntity]:
        """
        Processes all entries and returns a dictionary of canonical entities.
        """
        self.entities = {}
        
        # Group by name for deduplication
        name_groups: Dict[str, List[RawEntity]] = {}
        
        for line in raw_entries:
            entity = self.parse_raw_entry(line)
            if entity:
                key = entity.name.lower()
                if key not in name_groups:
                    name_groups[key] = []
                name_groups[key].append(entity)
        
        # Resolve each group
        for name, candidates in name_groups.items():
            if len(candidates) == 1:
                # Single entity - use as-is
                raw = candidates[0]
                self.entities[name] = CanonicalEntity(
                    id=f"{raw.name.lower()}_canonical",
                    name=raw.name,
                    roles=[raw.role] if raw.role else [],
                    attributes={
                        "status": raw.status,
                        "title": raw.title,
                        "authorship": [raw.authorship] if raw.authorship else []
                    },
                    merge_rationale="Single entry",
                    source_pages=raw.pages
                )
            else:
                # Multiple entries - need resolution logic
                # This is a placeholder for more complex merging logic
                self.entities[name] = CanonicalEntity(
                    id=f"{name}_merged",
                    name=name,
                    roles=[],
                    attributes={},
                    merge_rationale="Multiple entries require manual review",
                    source_pages=[]
                )
        
        return self.entities


def load_ars_notoria_data(filepath: str) -> List[str]:
    """
    Loads Ars Notoria data from a text file.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def save_entities(entities: Dict[str, CanonicalEntity], filepath: str):
    """
    Saves canonical entities to a JSON file.
    """
    data = []
    for name, entity in entities.items():
        data.append({
            "name": entity.name,
            "id": entity.id,
            "roles": entity.roles,
            "attributes": entity.attributes,
            "merge_rationale": entity.merge_rationale,
            "source_pages": entity.source_pages
        })
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    # Example usage
    resolver = EntityResolver()
    raw_entries = [
        "[ars_notoria] person: Solomon (role=recipient of revelation, status=proven) [14, 15, 23]",
        "[ars_notoria] person: Solomon (role=author, status=proven) [16, 17]"
    ]
    
    canonical = resolver.resolve_solomon_entities(raw_entries)
    print(f"Canonical Entity: {canonical.name}")
    print(f"Roles: {canonical.roles}")
    print(f"Rationale: {canonical.merge_rationale}")
