from pydantic import BaseModel
from typing import List

class PatientRequest(BaseModel):
    name: str
    age: int
    symptoms: List[str]
