from pydantic import BaseModel

class Experiment(BaseModel):
    name: str
    rank: int
    function: str
    appearance: str
    legion_count: int
    conjuration_method: str
    experiment_refs: list[str]
    page_folio_ref: str
    raw_quote: str
    chunk_id: str
    needs_verification: bool

class DataSchemas(BaseModel):
    spirit_experiments: list[Experiment]