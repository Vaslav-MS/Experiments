# Базовый образ
FROM python:3.12-slim

# Не создавать .pyc и буферизацию
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Создадим рабочую директорию
WORKDIR /app

# Установим системные зависимости (минимум)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# Скопируем только зависимостей для кеша слоёв
COPY requirements.txt .

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем исходники
COPY . .

# Команда запуска (polling; порт не нужен)
CMD [ "python", "bot.py" ]
