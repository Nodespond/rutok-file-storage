FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH="/app"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install -r requirements.txt
RUN pip install alembic psycopg2-binary

COPY . .

CMD ["python", "storage_service/main.py"]



