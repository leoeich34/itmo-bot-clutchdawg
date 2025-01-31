# app/langmodel/llm.py

import os
import re
import logging
import openai
import asyncio
from typing import Optional

from app.models.schemas import ResponseModel
from app.search.srch import google_search
from app.rssnews.news import get_latest_news
from app.utils.utilite import extract_options

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Подхватываем из .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.vsegpt.ru/v1")
MODEL_NAME = "gpt-4o-mini"  # Можно настроить через env или оставить так

# Конфигурация OpenAI
openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_API_BASE

def _call_chatgpt(messages: list, max_tokens=150, temperature=0.2) -> str:
    """
    Универсальная функция для генерации ответа через OpenAI ChatCompletion API.
    """
    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response["choices"][0]["message"]["content"].strip()
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API ошибка: {e}")
        return f"Ошибка генерации ответа: {e}"
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        return f"Неизвестная ошибка: {e}"

async def generate_response_async(query: str, request_id: int) -> ResponseModel:
    return await asyncio.to_thread(generate_response, query, request_id)

def generate_response(query: str, request_id: int) -> ResponseModel:
    """
    Генерирует ответ на основе запроса. Поддерживает как одиночные, так и
    многовариантные вопросы (с помощью функции extract_options).
    """
    options = extract_options(query)

    if options:
        # Вопрос с вариантами ответов
        answer, reasoning, sources = handle_multiple_choice(query, options)
    else:
        # Вопрос без вариантов ответов
        answer, reasoning, sources = handle_open_question(query)

    return ResponseModel(
        id=request_id,
        answer=answer,
        reasoning=reasoning,
        sources=sources
    )

def handle_multiple_choice(query: str, options: list):
    """
    Обрабатывает вопросы с вариантами ответов.
    Принимает список кортежей вида (номер, текст_варианта).
    """
    # Сначала попросим ChatGPT выбрать вариант (только одну цифру).
    messages = [
        {"role": "system", "content": "Вы — интеллектуальный помощник."},
        {"role": "user", "content": (
            f"Вопрос: {query}\n\n"
            "Выбери правильный вариант ответа (от 1 до 10). "
            "Отвечай только одной цифрой без пояснений."
        )}
    ]
    raw_output = _call_chatgpt(messages, max_tokens=10, temperature=0.0)
    raw_output = raw_output.strip()

    match = re.search(r"\b([1-9]|10)\b", raw_output)
    if match:
        answer = int(match.group(1))
    else:
        answer = None  # Не смогли распознать цифру


    reasoning_messages = [
        {"role": "system", "content": "Вы — интеллектуальный помощник."},
        {"role": "user", "content": (
            f"Объясни, почему {answer} является правильным ответом на этот вопрос:\n\n{query}"
        )}
    ]
    reasoning_raw = _call_chatgpt(reasoning_messages, max_tokens=80)
    reasoning = f"Использованная модель: {MODEL_NAME}. {reasoning_raw}"

    # Дополнительно возьмём источники из Google
    sources = google_search(query)[:3]

    return answer, reasoning, sources

def handle_open_question(query: str):
    messages = [
        {"role": "system", "content": "Вы — интеллектуальный помощник, предоставляющий краткую информацию об Университете ИТМО."},
        {"role": "user", "content": (
            f"Вопрос об Университете ИТМО:\n{query}\n\n"
            "Дай развернутый ответ, состоящий не более чем из двух предложений."
        )}
    ]
    raw_answer = _call_chatgpt(messages, max_tokens=80, temperature=0.2)
    raw_answer = f"Использованная модель: {MODEL_NAME}. {raw_answer}"

    # Получим источники через Google
    sources = google_search(query)

    # Если вопрос о новостях
    if "новость" in query.lower() or "news" in query.lower():
        latest_news = get_latest_news()
        sources.extend(latest_news)

    sources = sources[:3]
    return None, raw_answer, sources