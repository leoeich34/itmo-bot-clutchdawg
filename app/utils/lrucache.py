# app/utils/cache.py
# мой курсач кстати был по этой теме
from functools import lru_cache

@lru_cache(maxsize=1024)
def cached_generate_response(query: str, request_id: int) -> ResponseModel:
    # Логика генерации ответа
    return generate_response(query, request_id)