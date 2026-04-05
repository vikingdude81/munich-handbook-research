# scripts/validate_spirits.py
import os
from typing import List, Dict

def validate_spirits(spirits: List[dict]) -> None:
    seen_names = set()
    for spirit in spirits:
        if not isinstance(spirit, dict):
            raise ValueError("Each spirit must be a dictionary")
        
        required_fields = ["name", "rank", "provenance", "raw_quote"]
        for field in required_fields:
            if field not in spirit:
                raise ValueError(f"Missing required field: {field}")
        
        if spirit["name"] in seen_names:
            raise ValueError("Name must be unique")
        
        provenance = spirit.get("provenance")
        if isinstance(provenance, dict):
            for key in ["chunk_id", "passage"]:
                if key not in provenance:
                    raise ValueError(f"Missing required field in provenance: {key}")
        
        needs_verification = spirit.get("needs_verification")
        if needs_verification is True and "provenance" not in spirit or "passage" not in spirit["provenance"]:
            raise ValueError("NEEDS_VERIFICATION flag can only be set when passage is provided")

if __name-step_2__ == "__main__":
    spirits = load_spirits_from_file()
    validate_spirits(spirits)
