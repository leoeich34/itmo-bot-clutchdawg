# app/main.py

from fastapi import FastAPI, Request
from app.api import router
from dotenv import load_dotenv
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения из .env
load_dotenv()

# Проверяем, загружены ли ключи API
required_env_vars = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_CSE_ID"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Ошибка: отсутствуют переменные окружения: {', '.join(missing_vars)}")

app = FastAPI(
    title="ITMO University Chatbot",
    description="Бот для предоставления информации об Университете ИТМО",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    logger.info("Приложение запущено")

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в ITMO University Chatbot!"}

# Логирование всех запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Получен запрос: {request.method} {request.url}")
    try:
        body = await request.json()
        logger.info(f"Тело запроса: {body}")
    except Exception as e:
        logger.error(f"Ошибка при чтении тела запроса: {e}")
    response = await call_next(request)
    return response

# Подключаем роутер API
app.include_router(router)