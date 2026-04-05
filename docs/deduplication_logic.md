# Deduplication Logic (Heavy Tier)

## Normalization
1. Convert names to lowercase, remove spaces, and standardize titles (e.g., "Spirit of the Forest" → "spiritoftheforest").
2. Include title fields in normalization for better accuracy.

## Fuzzy Matching
- Use Levenshtein distance or cosine similarity with a threshold (e.g., 0.8) to identify duplicates.
- If normalized name + title matches an existing entry, mark as duplicate.

## Phase 2 Parser Pseudocode
```
ParseInput:
   For each entry in input:
      Parse name and title
      Normalize(name) → norm_name
      Normalize(title) → norm_title
      Compute similarity score (e.g., Levenshtein distance)
      Check against existing entries using (norm_name, norm_title)
      If duplicate:
         Mark as "Duplicate" and skip
      Else:
         Add to output with status="Unique"
```

## Key Features
- Heavy-tier logic includes advanced fuzzy matching and title-based normalization.
- Ensures consistency across chunks while handling edge cases like case insensitivity or partial matches.
