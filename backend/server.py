import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import time

from dotenv import load_dotenv
from tornado import web, ioloop
import pika

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

MAX_RETRIES = 10
RETRY_DELAY = 3

RABBITMQ_USERNAME = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')


def connect_to_rabbitmq():
    
    for attempt in range(MAX_RETRIES):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='rabbitmq',
                credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
            ))
            logger.info('Успешное подключение к RabbitMQ.')
            return connection
        except pika.exceptions.AMQPConnectionError:
            logger.warning(
                f'Попытка подключения к RabbitMQ {attempt + 1}/{MAX_RETRIES} не удалась. '
                f'Повтор через {RETRY_DELAY} секунд.'
            )
            time.sleep(RETRY_DELAY)
    raise Exception('Не удалось подключиться к RabbitMQ после нескольких попыток.')


class RabbitMQConnection:
    def __init__(self):
        self.connection = connect_to_rabbitmq()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='queue_appeal')

    def publish(self, data):
        self.channel.basic_publish(exchange='', routing_key='queue_appeal', body=json.dumps(data))

    def close(self):
        if self.connection:
            self.connection.close()
            logger.info('Подключение к RabbitMQ закрыто.')


rabbitmq_connection = RabbitMQConnection()
executor = ThreadPoolExecutor()


class MainHandler(web.RequestHandler):
    def get(self):
        self.render('index.html')


class AppealHandler(web.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        logger.info(f'Данные от пользователя: {data}')
        executor.submit(rabbitmq_connection.publish, data)
        self.write({'status': 'success'})


def make_app():
    return web.Application(
        [(r'/', MainHandler), (r'/api/request', AppealHandler)],
        template_path='templates',
    )


if __name__ == '__main__':
    logger.info('Start backend server!')
    app = make_app()
    app.listen(5000)
    try:
        ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        pass
    finally:
        rabbitmq_connection.close()
        executor.shutdown(wait=True)
