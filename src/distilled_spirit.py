from pydantic import BaseModel, Field

class DistilledSpirit(BaseModel):
    name: str = Field(..., description="Name of the distilled spirit")
    rank: int = Field(..., description="Rank of the spirit")
    function: str = Field(..., description="Function of the spirit")
    appearance: str = Field(..., description="Appearance of the spirit")
    legion_count: int = Field(..., description="Number of legions")
    conjuration_method: str = Field(..., description="Method to conjure the spirit")
    experiment_ref: str = Field(..., description="Experiment reference")
    page_folio: int = Field(..., description="Page folio number")
    raw_quote: str = Field(..., description="Raw quote from the spirit")
    needs_verification: bool | None = Field(None, description="Whether requires verification")