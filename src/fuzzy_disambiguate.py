import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pandas as pd
from rapidfuzz import process, fuzz

# Configuration Paths
BASE_DIR = r"E:\munich_handbook_research"
INPUT_FILE = os.path.join(BASE_DIR, "output", "writeback.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "output", "writeback_updated.json")
UNMATCHED_LOG = os.path.join(BASE_DIR, "unmatched_entities.json")

def load_munich_entities() -> pd.DataFrame:
    """
    Loads the canonical Munich entities list to serve as the reference for fuzzy matching.
    Adjust this path if your Munich data is stored elsewhere.
    """
    # Assuming a standard Munich format (e.g., from a previous step or a static file)
    # If Munich data is in a database, replace this with a db query.
    munich_path = os.path.join(BASE_DIR, "data", "munich_entities.json")
    
    if not os.path.exists(munich_path):
        # Fallback: Create a mock Munich list based on the source context provided in the prompt
        # to ensure the code runs immediately for testing.
        print("Munich canonical file not found. Using fallback canonical list from source context.")
        return pd.DataFrame([
            {"id": "solomon", "name": "Solomon", "alias": "King Solomon", "role": "recipient of revelation"},
            {"id": "apollonius", "name": "Apollonius", "alias": "Apollonius Tyana", "role": "master of arts"},
            {"id": "manichaeus", "name": "Manichaeus", "alias": "Mani", "role": "co-authority cited"},
            {"id": "euduchaeus", "name": "Euduchaeus", "alias": "Eudochius", "role": "co-authority cited"},
            {"id": "most_high_creator", "name": "Most High Creator", "alias": "God", "role": "source of revelation"},
        ])
    
    df = pd.read_json(munich_path)
    return df

def fuzzy_disambiguate(entity_str: str, candidates: pd.DataFrame, threshold: int = 85) -> Tuple[str, Optional[Dict]]:
    """
    Performs fuzzy matching against the Munich entities list.
    
    Args:
        entity_str: The string from the 'Not Found' entry (e.g., "person: Apollonius").
        candidates: DataFrame containing canonical Munich entities.
        threshold: Minimum similarity score (0-100) to consider a match. Default 85.
    
    Returns:
        Tuple of (status, matched_entity_dict). 
        status is 'Fuzzy Match' or None.
    """
    # Clean the input string for matching (remove prefixes like "person: ", "divine_name: ")
    clean_input = entity_str.replace("person: ", "").replace("divine_name: ", "").replace("spirit: ", "").strip()
    
    if not clean_input:
        return ("Unmatched", None)

    # Use rapidfuzz process.extract to find the best match
    # score_cutoff=0 ensures we get results even if low, but we filter later.
    matches = process.extract(
        query=clean_input, 
        choices=candidates["name"].tolist() + [c.get("alias", "") for c in candidates.to_dict('records')], 
        scorer=fuzz.WRatio, # Weighted ratio is usually better for names than simple ratio
        limit=1,
        score_cutoff=threshold
    )

    if matches and matches[0]["score"] >= threshold:
        matched_name = matches[0]["sequence"]
        # Find the actual record in the dataframe
        record = candidates[(candidates["name"] == matched_name) | (candidates["alias"] == matched_name)].iloc[0] if not candidates.empty else None
        return ("Fuzzy Match", record.to_dict() if record is not None else None)
    
    return ("Unmatched", None)

def process_writeback():
    """
    Main function to process writeback.json and apply fuzzy disambiguation.
    """
    # Load Munich entities
    munich_df = load_munich_entities()
    
    # Load writeback data
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        return
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        writeback_data = json.load(f)
    
    # Process each entry
    updated_entries = []
    unmatched_log = []
    
    for entry in writeback_data.get("entries", []):
        original_entry = entry.copy()
        status = "Found"
        matched_entity = None
        
        if entry.get("status") == "Not Found":
            # Apply fuzzy disambiguation
            result = fuzzy_disambiguate(entry["name"], munich_df)
            status, matched_entity = result
            
            if status == "Fuzzy Match" and matched_entity:
                entry["status"] = "Fuzzy Match"
                entry["matched_entity"] = matched_entity
                entry["confidence_score"] = result[0]["score"]
            else:
                # Log unmatched entries for manual review
                unmatched_log.append({
                    "original_entry": original_entry,
                    "reason": status,
                    "timestamp": pd.Timestamp.now().isoformat()
                })
        
        updated_entries.append(entry)
    
    # Save updated writeback
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({"entries": updated_entries}, f, indent=2, ensure_ascii=False)
    print(f"✅ Updated writeback saved to: {OUTPUT_FILE}")
    
    # Save unmatched log
    if unmatched_log:
        with open(UNMATCHED_LOG, 'w', encoding='utf-8') as f:
            json.dump({"unmatched_entries": unmatched_log}, f, indent=2, ensure_ascii=False)
        print(f"⚠️ Unmatched entries logged to: {UNMATCHED_LOG} ({len(unmatched_log)} entries)")
    else:
        print("✅ All entries were successfully disambiguated.")

if __name__ == "__main__":
    process_writeback()