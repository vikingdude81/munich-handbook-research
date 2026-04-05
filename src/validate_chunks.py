"""
Validate distilled chunk files and identify which ones need re-processing.

This script checks each JSON file for required fields and tracks which chunks
have been successfully processed vs. which need to be re-run through batch_distill_source.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set

# Required fields for valid spirit/distillation chunks
REQUIRED_FIELDS = [
    "spirit_names",
    "ranks",
    "functions",
    "appearances",
    "legion_counts",
    "conjuration_methods",
    "experiment_refs",
    "page_folio",
    "raw_quote"
]

def load_manifest(project_root: str) -> Dict:
    """Load RESEARCH_MANIFEST.md to understand current state."""
    manifest_path = Path(project_root) / "RESEARCH_MANIFEST.md"
    if not manifest_path.exists():
        return {}
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse manifest for chunk tracking info
    chunks_info = {}
    for line in content.split('\n'):
        if line.strip().startswith('chunk_') or 'file_' in line:
            chunks_info[line.strip()] = True
    
    return {
        "total_chunks": 39,
        "chunks_info": chunks_info
    }

def validate_chunk_file(filepath: str) -> Dict:
    """Validate a single chunk JSON file."""
    result = {
        "filepath": filepath,
        "valid": False,
        "errors": [],
        "missing_fields": []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if it's a dict
        if not isinstance(data, dict):
            result["errors"].append("Not a JSON object")
            return result
        
        # Check for required fields
        missing = []
        for field in REQUIRED_FIELDS:
            if field not in data or data[field] is None:
                missing.append(field)
        
        if missing:
            result["missing_fields"] = missing
            result["errors"].append(f"Missing fields: {', '.join(missing)}")
        else:
            result["valid"] = True
            result["data"] = data
        
    except json.JSONDecodeError as e:
        result["errors"].append(f"Invalid JSON syntax: {str(e)}")
    except Exception as e:
        result["errors"].append(f"Error reading file: {str(e)}")
    
    return result

def get_distillation_dir(project_root: str) -> Path:
    """Get the directory containing distilled chunk files."""
    # Common locations for distilled chunks
    possible_dirs = [
        project_root,
        os.path.join(project_root, "distilled"),
        os.path.join(project_root, "chunks"),
        os.path.join(project_root, "src", "distilled")
    ]
    
    for dir_path in possible_dirs:
        path = Path(dir_path)
        if path.exists() and any(f.endswith('.json') for f in path.iterdir()):
            return path
    
    # Default to project root
    return Path(project_root)

def find_invalid_chunks(distillation_dir: Path) -> List[str]:
    """Find all invalid chunk files."""
    invalid_files = []
    
    for json_file in distillation_dir.glob("*.json"):
        result = validate_chunk_file(str(json_file))
        if not result["valid"]:
            invalid_files.append({
                "filepath": result["filepath"],
                "errors": result["errors"],
                "missing_fields": result.get("missing_fields", [])
            })
    
    return invalid_files

def generate_retry_command(chunk_id: str) -> str:
    """Generate the batch_distill_source command for a specific chunk."""
    # This would be the actual command based on your setup
    return f"batch_distill_source --chunk-id {chunk_id} --model 120B-Thinker"

def main():
    """Main validation function."""
    project_root = r"E:\munich_handbook_research"
    
    print(f"Validating distilled chunks in: {project_root}")
    print("=" * 60)
    
    # Load manifest for context
    manifest = load_manifest(project_root)
    print(f"Manifest loaded. Total chunks expected: {manifest.get('total_chunks', 'N/A')}")
    
    # Get distillation directory
    distillation_dir = get_distillation_dir(project_root)
    print(f"Looking for chunk files in: {distillation_dir}")
    
    # Find invalid chunks
    invalid_files = find_invalid_chunks(distillation_dir)
    
    if not invalid_files:
        print("\n✓ All chunk files are valid!")
        return
    
    print(f"\nFound {len(invalid_files)} invalid chunk file(s):")
    print("=" * 60)
    
    for i, invalid in enumerate(invalid_files, 1):
        filepath = Path(invalid["filepath"])
        filename = filepath.name
        
        print(f"\n[{i}] {filename}")
        print("    Errors:")
        for error in invalid["errors"]:
            print(f"      - {error}")
        if invalid.get("missing_fields"):
            print(f"    Missing fields: {', '.join(invalid['missing_fields'])}")
        
        # Extract chunk ID from filename
        chunk_id = filename.replace("file_", "").replace(".json", "")
        retry_cmd = generate_retry_command(chunk_id)
        print(f"    Retry command: {retry_cmd}")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATION:")
    print("Run batch_distill_source on each invalid chunk ID to regenerate valid content.")
    print("After regeneration, re-run this script to verify all files are valid.")

if __name__ == "__main__":
    main()
