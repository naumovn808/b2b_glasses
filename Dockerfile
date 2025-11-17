FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY b2b_glasses/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/b2b_glasses

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]