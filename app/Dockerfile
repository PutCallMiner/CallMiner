FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src /app
COPY public /app/public

EXPOSE 8000

CMD ["sh", "-c", "fastapi $(if [ $ENV = 'development' ] ; then echo 'dev' ; else echo 'run'; fi) main.py --host 0.0.0.0 --port 8000" ]
