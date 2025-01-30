from typing import List, Optional
from pydantic import BaseModel

class RequestModel(BaseModel):
    query: str
    id: int

class ResponseModel(BaseModel):
    id: int
    answer: Optional[int]  # Используем Optional, чтобы разрешить значение null
    reasoning: str
    sources: List[str]