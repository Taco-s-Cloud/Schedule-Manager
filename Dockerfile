# Dockerfile for schedule-manager

FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

CMD ["python", "main.py"]
