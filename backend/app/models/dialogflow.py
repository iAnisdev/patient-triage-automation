from typing import List, Dict, Any
from pydantic import BaseModel

class QueryResult(BaseModel):
    parameters: Dict[str, Any]

class DialogflowWebhookRequest(BaseModel):
    queryResult: QueryResult
