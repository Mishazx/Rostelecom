from tornado import web, ioloop
import pika
import json
import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class AppealHandler(web.RequestHandler):
    def set_default_headers(self):
        # self.set_header("Access-Control-Allow-Origin", "https://rostelecom.mishazx.ru")
        self.set_header("Access-Control-Allow-Origin", "http://192.168.1.2:5000")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type')
        
    def post(self):
        data = json.loads(self.request.body)
        logger.info(data)
        connection = pika.BlockingConnection(pika.ConnectionParameters(    
            host='rabbitmq',
            credentials=pika.PlainCredentials('user', 'password')
        ))
        channel = connection.channel()
        channel.queue_declare(queue='requests')
        channel.basic_publish(exchange='', routing_key='requests', body=json.dumps(data))
        connection.close()
        self.write({"status": "success"})
        

def make_app():
    return web.Application([
        (r"/api/request", AppealHandler),
    ])

if __name__ == "__main__":
    logger.info('run backend')
    app = make_app()
    app.listen(5000)
    ioloop.IOLoop.current().start()
