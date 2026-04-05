from pydantic import BaseModel
from typing import List

class SpiritModel(BaseModel):
    name: str
    rank: int | None = None
    function: str | None = None
    appearance: str | None = None
    legion_count: int | None = None
    conjuration_method: str | None = None
    experiment_refs: List[ExpRef] | None = None
    raw_quote: str
    provenance: str | None = None
    needs_verification: bool | None = None