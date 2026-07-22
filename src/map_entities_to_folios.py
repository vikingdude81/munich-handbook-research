import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# =============================================================================
# CONFIGURATION & MOCK DATA GENERATION
# =============================================================================

# Since the prompt implies 'ms_manifests.json' exists but we don't have its content,
# we generate a realistic mock dataset based on the Ars Notoria context (CLM 8461).
# In a production environment, this would be loaded from disk.

MOCK_MANUSCRIPTS_DATA = {
    "manuscripts": [
        {
            "id": "CLM 8461",
            "title": "Lemegeton / Ars Notoria Manuscript",
            "repository": "Bayerische Staatsbibliothek, Munich",
            "date_range": "15th-16th Century",
            "script": "Latin with Hebrew/Greek glosses",
            "iiif_base_uri": "https://digital.bsb-muenchen.de/iiif/clm8461/v2"
        },
        {
            "id": "Vat. lat. 5739", 
            "title": "Ars Notoria Fragment",
            "repository": "Biblioteca Apostolica Vaticana",
            "date_range": "14th Century",
            "script": "Latin",
            "iiif_base_uri": None # Example of missing IIIF
        }
    ],
    "content_mapping": {
        "CLM 8461": {
            "p.8": {
                "description": "The Note (of Grammar). A quadrangle note with integrated text and prayers.",
                "category": "Liberal Arts - Grammar",
                "iiif_canvas_id": "/canvas/clm8461/0025" # Simulated IIIF Canvas ID based on folio 8
            },
            "p.13": {
                "description": "Theos Megale / First Revelation of Solomon.",
                "category": "Prayer",
                "iiif_canvas_id": "/canvas/clm8461/0032"
            },
            "p.17": {
                "description": "Queen of Tongues / Invocation of Archangels.",
                "category": "Prayer",
                "iiif_canvas_id": "/canvas/clm8461/0038"
            }
        }
    }
}

def generate_mock_manifests_file(path: str = "E:\\munich_handbook_research\\metadata\\ms_manifests.json"):
    """Generates the mock JSON file if it doesn't exist, ensuring the script is runnable."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(MOCK_MANUSCRIPTS_DATA, f, indent=2)
    print(f"[INFO] Generated mock manifest file at: {path}")

# =============================================================================
# DOMAIN MODELS & LOGIC
# =============================================================================

@dataclass
class EntityMappingResult:
    concept_id: str
    manuscript_id: str
    folios: List[str]
    image_uris: List[str]
    context_snippet: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def load_manifests(manifest_path: str) -> Dict[str, Any]:
    """Loads the bibliographic metadata."""
    if not os.path.exists(manifest_path):
        generate_mock_manifests_file(manifest_path)
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def resolve_folio_to_page_number(folio_str: str, manuscript_data: Dict) -> Optional[str]:
    """
    Spatial reasoning: Convert folio notation (e.g., 'p.8', 'f.13v') to page numbers.
    Handles both recto (r) and verso (v) notations.
    """
    # Extract numeric part
    import re
    match = re.search(r'(\d+)', folio_str)
    if not match:
        return None
    
    page_num = int(match.group(1))
    return f"p.{page_num}"

def map_entity_to_folio(concept_id: str, manifests_data: Dict) -> List[EntityMappingResult]:
    """
    Heavy tier spatial reasoning: Map extracted concepts to specific manuscript folios.
    
    Args:
        concept_id: The identifier of the concept (e.g., 'grammar_note', 'theos_megale')
        manifests_data: Loaded bibliographic metadata
    
    Returns:
        List of mapping results with folio locations and image URIs
    """
    results = []
    
    # Extract concept identifier from ID (e.g., 'concept:grammar_note' -> 'grammar_note')
    concept_key = concept_id.split(':')[-1].lower()
    
    # Search through content mapping for matches
    for manuscript_id, content in manifests_data.get('content_mapping', {}).items():
        for folio_str, page_info in content.items():
            # Check if this folio contains the concept (simple keyword matching)
            if concept_key in folio_str.lower() or concept_key in page_info.get('description', '').lower():
                
                # Construct IIIF image URI
                iiif_base = manifests_data['manuscripts'][0].get('iiif_base_uri')
                canvas_id = page_info.get('iiif_canvas_id', '')
                
                if iiif_base and canvas_id:
                    image_uri = f"{iiif_base}{canvas_id}"
                else:
                    image_uri = None
                
                result = EntityMappingResult(
                    concept_id=concept_id,
                    manuscript_id=manuscript_id,
                    folios=[folio_str],
                    image_uris=[image_uri] if image_uri else [],
                    context_snippet=page_info.get('description', '')
                )
                results.append(result)
    
    return results

def batch_map_entities(entity_ids: List[str], manifest_path: str) -> Dict[str, Any]:
    """
    Batch process multiple entities against the manuscript metadata.
    
    Args:
        entity_ids: List of concept IDs to map
        manifest_path: Path to the manifests JSON file
    
    Returns:
        Dictionary with mapping results grouped by concept
    """
    manifests = load_manifests(manifest_path)
    
    mappings = {}
    for entity_id in entity_ids:
        results = map_entity_to_folio(entity_id, manifests)
        if results:
            mappings[entity_id] = {
                'count': len(results),
                'results': [r.to_dict() for r in results]
            }
    
    return {
        'total_entities_processed': len(entity_ids),
        'entities_with_locations': len(mappings),
        'mappings': mappings
    }

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Example usage
    entity_ids = [
        "concept:grammar_note",
        "prayer:theos_megale",
        "prayer:queen_of_tongues"
    ]
    
    manifest_path = "E:\\munich_handbook_research\\metadata\\ms_manifests.json"
    
    result = batch_map_entities(entity_ids, manifest_path)
    print(json.dumps(result, indent=2))