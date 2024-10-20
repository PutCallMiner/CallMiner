FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt update
RUN apt install -y ffmpeg

RUN pip install --no-cache-dir -r requirements.txt

COPY webapp /app/webapp
COPY public /app/public

CMD ["sh", "-c", "uvicorn webapp.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload"]
