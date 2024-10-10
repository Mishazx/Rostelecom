import os
import time
import json
import logging

import pika
import psycopg2
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

MAX_RETRIES = 10
RETRY_DELAY = 3

DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'postgres')

RABBITMQ_USERNAME = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')

def connect_to_database():
    for attempt in range(MAX_RETRIES):
        try:
            connection = psycopg2.connect(        
                user=DB_USER,
                password=DB_PASSWORD,
                host='db',
                dbname=DB_NAME
            )
            logger.info("Успешное подключение к базе данных.")
            return connection
        except psycopg2.OperationalError:
            logger.warning(f"Попытка подключения к базе данных {attempt + 1}/{MAX_RETRIES} не удалась. "
                           f"Повтор через {RETRY_DELAY} секунд.")
            time.sleep(RETRY_DELAY)
    raise Exception("Не удалось подключиться к базе данных после нескольких попыток.")


def connect_to_rabbitmq():
    for attempt in range(MAX_RETRIES):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='rabbitmq',
                credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
            ))
            logger.info("Успешное подключение к RabbitMQ.")
            return connection
        except pika.exceptions.AMQPConnectionError:
            logger.warning(f"Попытка подключения к RabbitMQ {attempt + 1}/{MAX_RETRIES} не удалась. "
                           f"Повтор через {RETRY_DELAY} секунд.")
            time.sleep(RETRY_DELAY)
    raise Exception("Не удалось подключиться к RabbitMQ после нескольких попыток.")

def validate_data(data):
    required_keys = ['lastname', 'firstname', 'middlename', 'phone', 'message']
    for key in required_keys:
        if key not in data:
            logger.error(f"Отсутствует обязательный ключ: {key}")
            return False
    return True

class Service:
    def __init__(self):
        self.db_connection = connect_to_database()
        self.rabbitmq_connection = connect_to_rabbitmq()
        self.rabbitmq_channel = self.rabbitmq_connection.channel()
        self.rabbitmq_channel.queue_declare(queue='queue_appeal')
        self.rabbitmq_channel.basic_consume(queue='queue_appeal', on_message_callback=self.callback, auto_ack=True)

    def callback(self, ch, method, properties, body):
        data = json.loads(body)
        
        if not validate_data(data):
            logger.error('Некорректные данные, пропуск записи в БД.')
            return
        
        cur = self.db_connection.cursor()
        try:
            cur.execute("SELECT to_regclass('public.appeal');")
            table_exists = cur.fetchone()[0] is not None
            
            if not table_exists:
                logger.error('Таблица "appeal" не найдена.')
                return

            cur.execute("INSERT INTO appeal (lastname, firstname, middlename, phone, message) VALUES (%s, %s, %s, %s, %s)",
                        (data['lastname'], data['firstname'], data['middlename'], data['phone'], data['message']))
            self.db_connection.commit()
            logger.info('Данные записаны в БД')
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'Ошибка при записи в БД: {error}')
            self.db_connection.rollback()
        finally:
            cur.close()
            

    def start(self):
        try:
            logger.info('Start service!')
            self.rabbitmq_channel.start_consuming()
        except Exception as e:
            logger.error(f'Произошла ошибка: {e}')
        finally:
            self.stop()
        
        
    def stop(self):
        logger.info('Завершение работы службы...')
        self.rabbitmq_channel.stop_consuming()
        if self.rabbitmq_connection:
            self.rabbitmq_connection.close()
            logger.info('Подключение к RabbitMQ закрыто.')
        if self.db_connection:
            self.db_connection.close()
            logger.info('Подключение к базе данных закрыто.')

if __name__ == "__main__":
    service = Service()
    service.start()
