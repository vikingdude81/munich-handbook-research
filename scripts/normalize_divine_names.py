import json
import os
from typing import Dict, List, Tuple

# Configuration for output path
OUTPUT_DIR = r"E:\munich_handbook_research\data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "divine_names_canonical.json")


def normalize_string(text: str) -> str:
    """
    Normalizes spelling variants found in the source text.
    - Converts 'ae' to 'æ' for consistency (or standardizes to 'ae' if preferred).
      Here we standardize to lowercase and handle common OCR/translation typos.
    - Removes excessive whitespace.
    """
    if not text:
        return text
    
    # Lowercase for comparison, but we will preserve the "canonical" casing in the output
    # based on the most frequent or authoritative form found in the source logic.
    
    # Step 1: Normalize specific spelling variants mentioned in requirements
    # 'ae' often appears as 'æ' or 'e'. We standardize to 'ae' for readability unless 
    # a specific archaic form is requested, but here we stick to the text's dominant style.
    # The prompt asks to normalize 'z'/'s' and 'ae'/'æ'.
    
    # Replace 'æ' with 'ae' if present (standardizing ligatures)
    text = text.replace('æ', 'ae')
    
    # Normalize 'z' and 's' variants if they appear as distinct roots, 
    # but usually in these texts, they are distinct letters. 
    # However, the prompt implies mapping variants. We will create a canonical form 
    # by choosing the most frequent spelling from the provided context or a standard convention.
    # For this specific dataset, 'Assay' and 'Azzay' appear. We will treat them as variants 
    # of a root name.
    
    return text.strip()


def get_canonical_name(name: str) -> Tuple[str, str]:
    """
    Determines the canonical form for a given divine name based on linguistic patterns
    and the specific source data provided (Ars Notoria).
    
    Logic:
    1. The text provides specific compound names like 'Assaylemath Assay Lemath Azzabue'.
    2. Variants like 'Azzay' vs 'Assay' exist. We define a canonical root based on the 
       most complete or frequent form in the source context (often 'Assay' or 'Azzay').
       Given the prompt's instruction to map variants, we will select the form that 
       appears most consistently as the "root" or use the first occurrence if ambiguous.
       
    Simplified Logic for this specific dataset:
    - If the name contains 'Azzabue', it is a variant of 'Azzabue'.
    - If the name contains 'Assay', it is a variant of 'Assay'.
    
    We will implement a mapping based on the most "complete" or "standard" spelling 
    found in the provided snippets, preferring 'Assay' over 'Azzay' if they are roots,
    but keeping suffixes like 'Lemath', 'Azacgessenio' intact.
    
    Actually, looking at the data:
    - 'Assaylemath Assay Lemath Azzabue'
    - 'Azzaylemath Lemath Azacgessenio'
    
    These seem to be distinct parts of the Oration. The prompt asks to normalize 
    spelling variants (z/s, ae/æ).
    
    Strategy:
    1. Lowercase input for matching.
    2. Normalize 'ae' -> 'ae'.
    3. Normalize 'z' -> 's' OR 's' -> 'z'? The prompt says "normalize spelling variants".
       In Ars Notoria, the names are often considered sacred and specific. However, 
       if we must normalize:
       - 'Azzay' vs 'Assay': We will choose 'Assay' as the canonical form for roots
         that appear in both forms, based on frequency in historical texts.
    4. Preserve compound names like 'Lemath', 'Azacgessenio' as-is since they don't 
       have obvious variants in the source.
    """
    if not name:
        return (name, name)
    
    # Normalize the input string first
    normalized = normalize_string(name)
    
    # Define canonical mappings for known variants
    variant_mappings = {
        'azzay': 'assay',
        'azzailement': 'assaillement',
        'azzabue': 'assabue',
        'azacgessenio': 'asacgessenio',
    }
    
    # Check if the name (lowercased) matches any variant
    lower_name = normalized.lower()
    canonical = None
    
    for variant, canonical_form in variant_mappings.items():
        if variant in lower_name:
            canonical = canonical_form
            break
    
    # If no mapping found, use the normalized name as-is
    if canonical is None:
        canonical = normalized
    else:
        # Preserve original casing but apply canonical spelling
        # This is a simplified approach - in production, you'd want more sophisticated logic
        canonical = canonical.capitalize()
    
    return (normalized, canonical)


def process_source_text(source_text: str) -> List[Dict[str, str]]:
    """
    Processes source text to extract and normalize divine names.
    
    Args:
        source_text: Raw text containing divine names.
    
    Returns:
        List of dictionaries with 'original' and 'canonical' forms.
    """
    results = []
    
    # Simple tokenization - in production, use proper NLP
    words = source_text.split()
    
    for word in words:
        original = word
        canonical, _ = get_canonical_name(word)
        
        if canonical != original:
            results.append({
                'original': original,
                'canonical': canonical
            })
    
    return results


def main():
    """Main entry point to process and normalize divine names."""
    # Sample source text (in production, read from file)
    sample_text = """
    Assaylemath Assay Lemath Azzabue
    Azzaylemath Lemath Azacgessenio
    The Queen of Tongues prayer invokes the divine names.
    """
    
    # Process the text
    normalized_names = process_source_text(sample_text)
    
    # Create output structure
    output_data = {
        'source_text': sample_text.strip(),
        'normalized_entries': normalized_names,
        'total_variants_found': len(normalized_names)
    }
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Write to JSON file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully processed divine names.")
    print(f"Found {len(normalized_names)} variants to normalize.")
    print(f"Output written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
