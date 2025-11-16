# 1. Берем официальный образ Python 3.12
FROM python:3.12-slim

# 2. Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Устанавливаем рабочую директорию
WORKDIR /app

# 4. Копируем requirements.txt ИЗ папки b2b_glasses
# (В соответствии с вашей структурой)
COPY b2b_glasses/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем ВЕСЬ проект (включая папку b2b_glasses)
COPY . .

# 6. --- ГЛАВНОЕ ИСПРАВЛЕНИЕ ---
# Меняем рабочую папку на ту, где лежит manage.py
WORKDIR /app/b2b_glasses
# ---

# 7. "Открываем" порт 8000
EXPOSE 8000

# 8. Команда по умолчанию
# (Она будет заменена Gunicorn'ом в docker-compose.yml,
# но это хороший "fallback" для тестов)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]