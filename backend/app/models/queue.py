from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QueueItem(BaseModel):
    id: str
    patient_name: str
    age: int
    symptoms: List[str]
    urgency: str
    timestamp: datetime
    status: str = "pending" 