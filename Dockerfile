FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "storage_service.main:app", "--host", "0.0.0.0", "--port", "8001"]