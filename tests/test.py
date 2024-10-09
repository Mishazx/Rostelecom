import os
import pytest
import requests
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

ENDPOINT_URL = 'http://localhost:5000/api/request'

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

RABBITMQ_USERNAME = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')

@pytest.mark.parametrize("url", [ENDPOINT_URL])
def test_multiple_requests(url):
    form_data = {
        "lastname": "Иванов",
        "firstname": "Иван",
        "middlename": "Иванович",
        "phone": "+79001234567",
        "message": "Тестовое сообщение"
    }
    for i in range(1000):
        response = requests.post(url, json=form_data)
        logging.info(f'Итерация {i + 1}, статус: {response.status_code}')
        assert response.status_code == 200, f"Ошибка: {response.status_code}, итерация: {i + 1}"


from ..servicedb.service import connect_to_rabbitmq

def test_multiple_queries():
    connection = connect_to_rabbitmq()
    
    
    print(connection)
    



if __name__ == '__main__':
    # pytest.main()
    test_multiple_queries()
