import pika
import json
import threading

RABBITMQ_USERNAME = 'guest'
RABBITMQ_PASSWORD = 'guest'
ENDPOINT_URL = 'http://localhost:5000/api/request/'

NUM_THREADS = 50

def send_messages(data, count):
    for _ in range(count):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost',
                credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
            ))
            channel = connection.channel()
            channel.queue_declare(queue='queue_appeal')
            channel.basic_publish(exchange='', routing_key='queue_appeal', body=json.dumps(data))
            connection.close()
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")

def test_multiple_requests(total_messages):
    data = {
        "lastname": "Иванов",
        "firstname": "Иван",
        "middlename": "Иванович",
        "phone": "+79001234567",
        "message": "Тестовое сообщение"
    }
    
    threads = []
    messages_per_thread = total_messages // NUM_THREADS
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=send_messages, args=(data, messages_per_thread))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

test_multiple_requests(100000)
