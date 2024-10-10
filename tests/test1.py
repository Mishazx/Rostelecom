import json
import os
import pika
import pytest
import requests
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

ENDPOINT_URL = 'http://localhost:5000/api/request'

RABBITMQ_USERNAME = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')

@pytest.mark.parametrize("url", [ENDPOINT_URL])
def test_multiple_requests(url):
    data = {
        "lastname": "Иванов",
        "firstname": "Иван",
        "middlename": "Иванович",
        "phone": "+79001234567",
        "message": "Тестовое сообщение"
    }
    for i in range(1000):
        connection = pika.BlockingConnection(pika.ConnectionParameters(    
            host='localhost',
            credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
        ))
        channel = connection.channel()
        channel.queue_declare(queue='queue_appeal')
        channel.basic_publish(exchange='', routing_key='queue_appeal', body=json.dumps(data))
        connection.close()
        assert connection.is_closed == True, f"Connection not closed, iteration: {i + 1}"
    
        # logging.info(f'Итерация {i + 1}, статус: {connection.close()}')
        # assert response.status_code == 200, f"Ошибка: {response.status_code}, итерация: {i + 1}"
        
        
if __name__ == '__main__':
    pytest.main()
    test_multiple_requests(ENDPOINT_URL)
    # test_multiple_queries()


    # for i in range(1000):
    #     response = requests.post(url, json=form_data)
    #     logging.info(f'Итерация {i + 1}, статус: {response.status_code}')
    #     assert response.status_code == 200, f"Ошибка: {response.status_code}, итерация: {i + 1}"


# from ..servicedb.service import connect_to_rabbitmq

# def test_multiple_queries():
    # connection = connect_to_rabbitmq()
    
    
    # print(connection)
    



# @pytest.mark.parametrize("url", [ENDPOINT_URL])
# def test_multiple_requests(url):
#     form_data = {
#         "lastname": "Иванов",
#         "firstname": "Иван",
#         "middlename": "Иванович",
#         "phone": "+79001234567",
#         "message": "Тестовое сообщение"
#     }
#     for i in range(1000):
#         response = requests.post(url, json=form_data)
#         logging.info(f'Итерация {i + 1}, статус: {response.status_code}')
#         assert response.status_code == 200, f"Ошибка: {response.status_code}, итерация: {i + 1}"
