from fastapi import FastAPI
from app.api import router
from dotenv import load_dotenv
import os

load_dotenv()  # Загрузка переменных из .env

app = FastAPI(
    title="ITMO University Chatbot",
    description="Бот для предоставления информации об Университете ИТМО",
    version="1.0.0"
)

app.include_router(router)