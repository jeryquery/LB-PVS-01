FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY aapl_consumer.py .

CMD ["python", "aapl_consumer.py"]