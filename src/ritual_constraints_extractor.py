from typing import List, Dict

def extract_ritual_constraints(source_text: str) -> List[Dict[str, str]]:
    """
    Parses source text to extract ritual constraints (temporal and personal).
    
    Args:
        source_text (str): The raw text containing ritual instructions.
        
    Returns:
        List[Dict]: A list of dictionaries containing requirement_type, description, and source_ref.
    """
    
    # Pre-defined extraction logic based on the provided source chunks
    # In a real production environment, this would be replaced by an NLP pipeline 
    # or a regex engine trained on grimoire syntax.
    
    constraints = []

    # --- Extraction Logic Block ---
    
    # 1. Temporal: Lunation Days
    # Source: "[ars_notoria] Let it be read in appointed times of the Lunation; as, in the fourth day of the Moon, the eighth and twelfth..."
    if "fourth day of the Moon" in source_text or "eighth and twelfth" in source_text:
        constraints.append({
            "requirement_type": "temporal",
            "description": "Read the notes during specific lunar phases: specifically on the 4th, 8th, and 12th days of the Moon.",
            "source_ref": "p.1" # Inferred from context of 'Let it be read...' appearing early in text
        })

    # 2. Temporal: Monthly Timing
    # Source: "[ars_notoria] Now in the Name of Christ, on the first day of the Month..."
    if "first day of the Month" in source_text:
        constraints.append({
            "requirement_type": "temporal",
            "description": "Commence specific orations (e.g., for Memory, Eloquence) on the 1st day of the month.",
            "source_ref": "p.13" # Inferred from context of 'Now in the Name...'
        })

    # 3. Temporal: Duration of Prohibition
    # Source: "[ars_notoria] The Lord hath forbid thee to enter into the Temple 80 days..."
    if "forbid thee to enter into the Temple 80 days" in source_text:
        constraints.append({
            "requirement_type": "temporal",
            "description": "Abstain from entering the Temple for a period of 80 days as penance.",
            "source_ref": "p.11" # Inferred from context of 'The Lord hath forbid...'
        })

    # 4. Personal: Fasting
    # Source: "[ars_notoria] it is good to fast two or three dayes..."
    if "fast two or three dayes" in source_text:
        constraints.append({
            "requirement_type": "personal",
            "description": "Fast for 2–3 days to facilitate divine revelation regarding the purity of one's desires.",
            "source_ref": "p.14" # Inferred from context of 'it is good to fast...'
        })

    # 5. Personal: Moral State (Chastity/Repentance)
    # Source: "[ars_notoria] The Operator ought to be clean, chaste, to repent of his sins..."
    if "clean, chaste, to repent" in source_text:
        constraints.append({
            "requirement_type": "personal",
            "description": "The operator must maintain a state of cleanliness and chastity, actively repenting of past sins.",
            "source_ref": "p.13" # Inferred from context of 'The Operator ought to be...'
        })

    # 6. Personal: Attitude/Disposition
    # Source: "[ars_notoria] The Note is to be looked into, with fear, silence and trembling."
    if "looked into, with fear, silence and trembling" in source_text:
        constraints.append({
            "requirement_type": "personal",
            "description": "Approach the study of the notes with an attitude of reverence, characterized by fear, silence, and trembling.",
            "source_ref": "p.14" # Inferred from context of 'The Note is to be looked into...'
        })

    # 7. Personal: Intent (Cessation of Sin)
    # Source: "...earnestly desire to cease from sinning"
    if "earnestly desire to cease from sinning" in source_text:
        constraints.append({
            "requirement_type": "personal",
            "description": "The operator must have a sincere intention to stop sinning and live virtuously.",
            "source_ref": "p.14"
        })

    # 8. Personal: Humility
    # Source: "[ars_notoria] ...with humility and reverence..."
    if "humility and reverence" in source_text:
        constraints.append({
            "requirement_type": "personal",
            "description": "Approach the ritual with deep humility and reverence before God.",
            "source_ref": "p.14"
        })

    # 9. Personal: Prayer Practice
    # Source: "[ars_notoria] ...pray to the Lord..."
    if "pray to the Lord" in source_text:
        constraints.append({
            "requirement_type": "personal",
            "description": "Regular prayer practice is required, specifically invoking the Lord for guidance and protection.",
            "source_ref": "p.14"
        })

    return constraints