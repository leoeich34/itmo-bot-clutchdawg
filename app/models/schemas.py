# app/models/schemas.py

from typing import List, Optional
from pydantic import BaseModel

class RequestModel(BaseModel):
    query: str
    id: int

class BatchRequestModel(BaseModel):
    requests: List[RequestModel]

class ResponseModel(BaseModel):
    id: int
    answer: Optional[int]
    reasoning: str
    sources: List[str]

class BatchResponseModel(BaseModel):
    responses: List[ResponseModel]