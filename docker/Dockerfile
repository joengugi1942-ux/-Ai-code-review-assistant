FROM python:3.11-slim

LABEL com.lapo.description="Lapo - AI Code Review Assistant"
LABEL com.lapo.version="0.1.0"

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]




