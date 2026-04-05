from dataclasses import dataclass

@dataclass
class Spirit:
    chunk_id: int
    passage_start: int
    raw_quote: str
    NEEDS_VERIFICATION: bool

@dataclass
class Provenance:
    chunk_id: int
    passage_start: int
    raw_quote: str
    NEEDS_VERIFICATION: bool
