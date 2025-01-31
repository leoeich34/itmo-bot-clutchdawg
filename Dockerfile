# Используем официальный Python образ с минимальным размером
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости, если необходимо
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip show openai

# Копируем код приложения
COPY . .

# Создаём непривилегированного пользователя для повышения безопасности
RUN adduser --no-create-home appuser
USER appuser

# Экспонируем порт, на котором будет работать приложение
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]