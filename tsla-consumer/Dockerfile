FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY tsla_consumer.py .

CMD ["python", "tsla_consumer.py"]