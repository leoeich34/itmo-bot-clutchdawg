# app/api.py

from fastapi import APIRouter, HTTPException
from typing import Union
from app.models.schemas import (
    RequestModel,
    BatchRequestModel,
    ResponseModel,
    BatchResponseModel
)
from app.langmodel.llm import generate_response_async
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/request", response_model=Union[ResponseModel, BatchResponseModel])
async def handle_request(body: Union[RequestModel, BatchRequestModel]):
    try:
        if isinstance(body, BatchRequestModel):
            tasks = [generate_response_async(req.query, req.id) for req in body.requests]
            responses = await asyncio.gather(*tasks)
            return BatchResponseModel(responses=responses)
        else:
            response = await generate_response_async(body.query, body.id)
            return response
    except HTTPException as http_exc:
        logger.error(f"HTTPException: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера.")