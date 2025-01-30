import openai
import os
from app.models.schemas import ResponseModel
from app.search.srch import google_search
from app.rssnews.news import get_latest_news
from app.utils.utilite import extract_options

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_response(query: str, request_id: int) -> ResponseModel:
    # Определяем, содержит ли запрос варианты ответов
    options = extract_options(query)
    if options:
        # Вопрос с вариантами
        answer, reasoning, sources = handle_multiple_choice(query, options)
    else:
        # Вопрос без вариантов
        answer, reasoning, sources = handle_open_question(query)

    return ResponseModel(
        id=request_id,
        answer=answer,
        reasoning=reasoning,
        sources=sources
    )


def handle_multiple_choice(query: str, options: list):
    prompt = f"Определи правильный вариант ответа на следующий вопрос:\n{query}\n\nОтветь только номером варианта."
    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=10,
        n=1,
        stop=None,
        temperature=0
    )
    answer_text = response.choices[0].text.strip()
    try:
        answer = int(answer_text)
    except ValueError:
        answer = -1  # Если не удалось определить

    # Получение объяснения и источников
    reasoning = "Ответ получен с помощью модели GPT-4."
    # Выполнение поиска для источников
    sources = google_search(query)
    return answer, reasoning, sources


def handle_open_question(query: str):
    prompt = f"Дай подробный ответ на следующий вопрос о Университете ИТМО:\n{query}"
    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7
    )
    reasoning = response.choices[0].text.strip()

    # Выполнение поиска для источников
    sources = google_search(query)

    # Если вопрос связан с новостями, добавляем последние новости
    if "новость" in query.lower() or "news" in query.lower():
        latest_news = get_latest_news()
        sources.extend(latest_news)
        # Ограничиваем до 3 ссылок
        sources = sources[:3]

    return None, reasoning, sources