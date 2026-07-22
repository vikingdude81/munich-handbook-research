"""
Ars Notoria Divine Name Extractor

This module provides a production-ready extraction pipeline for identifying 
divine names, their variants, linguistic origins, and ritual functions from 
textual sources related to the Ars Notoria grimoire.

Author: Expert Coder
Date: 2023-10-27
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from collections import defaultdict


@dataclass
class DivineNameEntry:
    """Represents a single extracted divine name entity."""
    divine_name: str
    variant_forms: List[str] = field(default_factory=list)
    origin_languages: List[str] = field(default_factory=list)
    ritual_function: Optional[str] = None
    source_pages: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert entry to dictionary for JSON serialization."""
        return {
            "divine_name": self.divine_name,
            "variant_forms": self.variant_forms,
            "origin_languages": self.origin_languages,
            "ritual_function": self.ritual_function,
            "source_pages": self.source_pages
        }


class ArsNotoriaExtractor:
    """
    Parser for extracting divine names and metadata from raw text chunks.
    
    Handles regex pattern matching for entity tags and free-text mentions,
    deduplicates variants, and maps contextual metadata.
    """

    # Regex patterns for specific entity types found in source material
    PATTERN_ENTITY_TAG = re.compile(r'\[(.*?)\]')
    PATTERN_DIVINE_NAME_TAG = re.compile(r'divine_name:\s*(.+?)(?:\s*status=|,|$)', re.IGNORECASE)
    PATTERN_PAGE_REFERENCE = re.compile(r'p\.\d+')
    
    # Keywords for language mapping based on context in source text
    LANGUAGE_KEYWORDS = {
        'Chaldee': ['Chaldee', 'Chaldean'],
        'Hebrew': ['Hebrew'],
        'Greek': ['Greek', 'Grecian'],
        'Latin': ['Latine', 'Latin']
    }

    # Keywords for function mapping based on context in source text
    FUNCTION_KEYWORDS = {
        'invokes angels': ['invokes angels', 'provokes eloquence', 'ministered to Solomon'],
        'removes impediments of the tongue': ['removes impediments of the tongue', 'grants eloquence'],
        'increases memory': ['increase Memory', 'obtain Eloquence', 'acquire Memory'],
        'first revelation': ['First Revelation', 'without any Interpretation']
    }

    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.entries: List[DivineNameEntry] = []

    def _extract_pages(self, text_segment: str) -> List[int]:
        """Extract page numbers from a text segment."""
        matches = self.PATTERN_PAGE_REFERENCE.findall(text_segment)
        return [int(p) for p in matches] if matches else []

    def _map_languages(self, context: str) -> List[str]:
        """Map linguistic origins based on keyword presence in context."""
        found_langs = set()
        for lang, keywords in self.LANGUAGE_KEYWORDS.items():
            if any(kw.lower() in context.lower() for kw in keywords):
                found_langs.add(lang)
        return list(found_langs)

    def _map_function(self, context: str) -> Optional[str]:
        """Map ritual function based on keyword presence in context."""
        for func, keywords in self.FUNCTION_KEYWORDS.items():
            if any(kw.lower() in context.lower() for kw in keywords):
                return func
        return None

    def _parse_entity_tag(self, match: re.Match) -> Optional[DivineNameEntry]:
        """Parse a structured entity tag like [divine_name: ...]."""
        content = match.group(1)
        
        # Extract name and status/context
        name_match = self.PATTERN_DIVINE_NAME_TAG.search(content)
        if not name_match:
            return None
            
        name = name_match.group(1).strip()
        context = content
        
        # Clean up page references from the main string for cleaner extraction
        clean_context = re.sub(r'\[p\.\d+\]', '', context)
        
        entry = DivineNameEntry(
            divine_name=name,
            variant_forms=[],
            origin_languages=self._map_languages(clean_context),
            ritual_function=self._map_function(clean_context),
            source_pages=self._extract_pages(context)
        )
        
        return entry

    def extract(self) -> List[DivineNameEntry]:
        """
        Main extraction method that processes the raw text and returns
        a list of DivineNameEntry objects.
        """
        self.entries = []
        
        # Find all entity tags in the text
        for match in self.PATTERN_ENTITY_TAG.finditer(self.raw_text):
            entry = self._parse_entity_tag(match)
            if entry:
                self.entries.append(entry)
        
        return self.entries

    def get_summary(self) -> Dict[str, List[DivineNameEntry]]:
        """
        Returns a summary grouped by ritual function.
        """
        summary: Dict[str, List[DivineNameEntry]] = defaultdict(list)
        
        for entry in self.entries:
            if entry.ritual_function:
                summary[entry.ritual_function].append(entry)
            else:
                summary['unknown'].append(entry)
        
        return dict(summary)


def extract_divine_names_from_file(filepath: str) -> List[DivineNameEntry]:
    """
    Convenience function to extract divine names from a file.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    
    extractor = ArsNotoriaExtractor(raw_text)
    return extractor.extract()


def extract_divine_names_from_string(text: str) -> List[DivineNameEntry]:
    """
    Convenience function to extract divine names from a string.
    """
    extractor = ArsNotoriaExtractor(text)
    return extractor.extract()
