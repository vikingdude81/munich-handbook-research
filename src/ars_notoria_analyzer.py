import re
import json
from typing import List, Dict, Any, Optional

class ArsNotoriaAnalyzer:
    """
    Analyzes source text for Ars Notoria entities (divine names, prayers)
    and extracts structured metadata into a JSON-compatible format.
    
    This class parses the specific entity definitions found in the distillation
    data, normalizing attributes like 'status', 'function', and 'origin' 
    to match the requested output schema.
    """

    def __init__(self, source_text: str):
        """
        Initialize the analyzer with the raw source text.
        
        Args:
            source_text (str): The full text content containing [ars_notoria] entities.
        """
        self.source_text = source_text

    def _extract_page_ref(self, line: str) -> Optional[str]:
        """
        Extracts page reference from the end of the line (e.g., [p.13]).
        
        Args:
            line (str): The raw text line to search.
            
        Returns:
            Optional[str]: The matched page reference string or None.
        """
        # Regex looks for pattern like [p.XX] at the end of the line
        match = re.search(r'\[(?:p\.\d+)\]', line)
        return match.group(0) if match else None

    def _parse_attributes(self, content: str) -> Dict[str, str]:
        """
        Parses key=value pairs from the attribute string.
        Handles values that might contain commas or spaces within parentheses.
        
        Args:
            content (str): The string inside the parentheses containing attributes.
            
        Returns:
            Dict[str, str]: A dictionary of parsed attributes.
        """
        attributes = {}
        # Pattern matches key=value where value is not followed by a closing paren immediately 
        # but allows for spaces and commas within the value.
        pattern = r'(\w+)=(.+?)(?:\s*\)|$)'
        
        for match in re.finditer(pattern, content):
            key = match.group(1).strip()
            value = match.group(2).strip()
            # Clean up the value (remove trailing spaces)
            attributes[key] = value.strip()
            
        return attributes

    def analyze(self) -> List[Dict[str, Any]]:
        """
        Main analysis logic. Iterates through lines, identifies entities,
        normalizes data to the requested JSON schema.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the extracted entities.
        """
        results = []
        
        # Filter lines starting with [ars_notoria] to focus on relevant sections
        for line in self.source_text.splitlines():
            if not line.strip().startswith('[ars_notoria]'):
                continue
            
            # Extract page reference first (often at end)
            page_ref = self._extract_page_ref(line)
            
            # Check for divine_name or prayer entity definition.
            # Expected format: [ars_notoria] type: Name (attributes) [page]
            # Regex breakdown:
            #   \[ars_notoria\] : Literal prefix filter
            #   (?:divine_name|prayer): Non-capturing group for entity type
            #   :\s*: Colon and optional whitespace
            #   (.+?): Captures the Name (non-greedy)
            #   \(.*?\): Captures content inside parentheses (attributes)
            #   \s*\[p\.\d+\]: Matches page reference at the end
            entity_match = re.search(
                r'\[(?:divine_name|prayer):\s*(.+?)\]\((.*?)\)\s*\[p\.\d+\]', 
                line
            )
            
            if not entity_match:
                # Skip lines that don't match the structured entity format
                continue

            name = entity_match.group(1).strip()
            attributes_str = entity_match.group(2)
            
            attrs = self._parse_attributes(attributes_str)
            
            # Normalize fields to requested schema keys
            # Mapping log
            result = {
                "entity_type": "divine_name" if "divine_name" in line else "prayer",
                "name": name,
                "attributes": attrs,
                "page_ref": page_ref
            }
            results.append(result)
        
        return results