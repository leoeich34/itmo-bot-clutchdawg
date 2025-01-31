# rag_agent.py

from typing import Dict
from app.rag.vector_db import VectorDB
from app.langmodel.llm import generate_response
from app.rag.embeddings import EmbeddingsModel
from app.search.srch import google_search  # для доп. поиска

class RAGAgent:
    def __init__(self):
        self.vector_db = VectorDB()
        self.vector_db.initialize_db()
        self.embed_model = EmbeddingsModel()

    # фанкшн обработки запроса
    async def process_query(self, query: str, request_id: int) -> Dict:
        # 1. Генерируем эмбеддинг для запроса
        query_emb = self.embed_model.get_embeddings([query])[0]

        # 2. Ищем релевантные данные в VectorDB
        rag_results = self.vector_db.query(query_emb)

        # Если полученных данных мало, можно проверить score, 
        # и если score < threshold — задействовать поиск
        if not rag_results or (rag_results and rag_results[0]["score"] < 0.3):
            # Выполнить поиск в Google
            search_links = google_search(query, num_results=3)
        else:
            search_links = []

        # 3. Формируем финальный промпт для LLM
        # Составляем контекст из rag_results, если есть.
        context_texts = [item["text"] for item in rag_results]
        context_combined = "\n---\n".join(context_texts)

        prompt = f"""
Вопрос: {query}
Контекст из RAG:
{context_combined}

Ссылки из веб-поиска (если есть):
{search_links}

Проанализируй вопрос и ответь в JSON-формате:
{{
    "id": {request_id},
    "answer": "Если вопрос с вариантами, укажи номер. Иначе null",
    "reasoning": "Твой развернутый ответ со ссылками или фактами.",
    "sources": ["Перечисли максимум 3 ссылки, если есть"]
}}
        """

        # 4. Получаем итоговый ответ из LLM
        final_response = await generate_response(prompt)

        # Вариант: final_response уже должен быть JSON-объектом, 
        # но вам придётся распарсить его и привести к схеме ResponseModel
        # Ниже — пример как это можно сделать, если generate_response возвращает text:
        import json
        try:
            response_dict = json.loads(final_response)
        except:
            # на случай ошибок
            response_dict = {
                "id": request_id,
                "answer": None,
                "reasoning": "Ошибка парсинга JSON",
                "sources": []
            }

        return response_dict

