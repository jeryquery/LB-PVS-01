import os
import pika
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus der .env-Datei
load_dotenv()


# Umgebungsvariablen laden RabbitMQ
rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "default_user")  
rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS", "default_pass")
rabbitmq_queue = os.getenv("RABBITMQ_QUEUE")

# Umgebungsvariablen laden MongoDB
mongodb_uri = os.getenv("MONGODB_URI")
mongodb_db = os.getenv("MONGODB_DB")
mongodb_collection = os.getenv("MONGODB_COLLECTION")

# Verbindung zu RabbitMQ herstellen
connection_params = pika.ConnectionParameters(
    host=rabbitmq_host,
    port=5672,
    credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
)
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()


# Verbindung zu MongoDB herstellen
client = MongoClient(mongodb_uri)
db = client[mongodb_db]
collection = db[mongodb_collection]

# Set Grösse definieren und Speicher für Price und Nachrichtenzähler
batch_size = 1000
price_sum = 0
message_count = 0

# Nachrichten Batch verarbeiten = Preis berechnen und db schreiben
def process_batch():
    global price_sum, message_count
    if message_count > 0:
        avg_price = price_sum / message_count
        print(f"Saving average price for {rabbitmq_queue}: {avg_price}")
        collection.insert_one({"company": "MSFT", "avgPrice": avg_price})

    # Nach Verarbeitung zurücksetzen
    price_sum = 0
    message_count = 0  


def callback(ch, method, properties, body):
    global price_sum, message_count

    #JSON File mit Werten auslesen
    message = json.loads(body.decode('utf-8'))
    event_type = message.get("eventType")
    price = message.get("price", 0)

    # Nur Buy berücksichtigen
    if event_type == "buy":
        price_sum += price
        message_count += 1

    # Nachrichten verarbeiten wenn 1000 erreicht sind.
    if message_count >= batch_size:
        process_batch()

# Nachrichten verarbeiten
channel.queue_declare(queue=rabbitmq_queue)
channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)

print(f'Waiting for {rabbitmq_queue} messages. To exit press CTRL+C')
try:
    channel.start_consuming()
except KeyboardInterrupt:
    # Behandle Restnachrichten, wenn das Programm beendet wird
    process_batch()
    print("Exiting...")