import os
import pika

class RabbitMQSender:
    def __init__(self, queue_name = 'default_queue') -> None:
        self.queue_name = queue_name
        self.conn_prm = pika.ConnectionParameters(
            host='rabbitmq',
            port=5672,
            virtual_host='/',
            credentials=pika.PlainCredentials(
                username=os.getenv('RABBITMQ_DEFAULT_USER', 'guest'),
                password=os.getenv('RABBITMQ_DEFAULT_PASSWORD', 'guest')
            ),
            heartbeat=30,
            blocked_connection_timeout=2
        )

    def open(self):
        self.connection = pika.BlockingConnection(self.conn_prm)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
    
    def close(self):
        if self.connection:
            self.connection.close()

    def __enter__(self) -> object:
        self.open()       
        return self
    
    def __exit__(self, *args, **kwargs):
        self.close()
    

    def send_task(self, message: str):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=message
        )

    