from fastapi import APIRouter, HTTPException
from app.models.schemas import RequestModel, ResponseModel
from app.langmodel.llm import generate_response
from app.search.srch import google_search
from app.rssnews.news import get_latest_news

router = APIRouter()
# POST-метод
@router.post("/api/request", response_model=ResponseModel)
async def handle_request(request: RequestModel):
    try:
        response = await generate_response(request.query, request.id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))