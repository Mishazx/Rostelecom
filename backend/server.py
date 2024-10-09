import os
import json
import logging

from tornado import web, ioloop
import pika
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

RABBITMQ_USERNAME = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')

class MainHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")

class AppealHandler(web.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        logger.info(f'данные от пользователя : {data}')
        connection = pika.BlockingConnection(pika.ConnectionParameters(    
            host='rabbitmq',
            credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
        ))
        channel = connection.channel()
        channel.queue_declare(queue='queue_appeal')
        channel.basic_publish(exchange='', routing_key='queue_appeal', body=json.dumps(data))
        connection.close()
        self.write({"status": "success"})
        

def make_app():
    return web.Application([
        (r"/", MainHandler),
        (r"/api/request", AppealHandler),
    ],
    template_path="templates")

if __name__ == "__main__":
    logger.info('Запуск backend сервера')
    app = make_app()
    app.listen(5000)
    ioloop.IOLoop.current().start()
