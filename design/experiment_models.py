from pydantic import BaseModel, Field
from enum import Enum

class Rank(str, Enum):
    high = "high"
    middle = "middle"
    lower = "lower"

class Provenance(BaseModel):
    source: str = Field(..., description="Source of the data")
    date: str = Field(..., description="Date when the data was sourced")

class VerificationFlag(BaseModel):
    status: bool = True
    reason: str | None = None

class Experiment(BaseModel):
    id: int = Field(..., description="Unique identifier for the experiment")
    name: str = Field(..., min_length=1, max_length=256, description="Name of the experiment")
    rank: Rank = Field(Rank.middle, description="Ranking of the experiment (high, middle, lower)")
    provenance: Provenance = Field(default_factory=Provenance, description="Details about where the data came from")
    verification_flag: VerificationFlag | None = Field(None, description="Verification status and reason for the experiment")
