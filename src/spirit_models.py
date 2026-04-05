from pydantic import BaseModel
from typing import Optional

class DistilledSpirit(BaseModel):
    name: str
    type: str
    alcohol_content: float
    needs_verification: Optional[bool] = False