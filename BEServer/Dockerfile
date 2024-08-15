FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./be /app/

CMD ["sh", "-c", "uvicorn be.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload"]
