import pika
import json
import logging
import time
from app.config import Config

logger = logging.getLogger(__name__)

class MessageQueue:
    def __init__(self):
        self.connect()
        
    def connect(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(Config.RABBITMQ_URL)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=Config.QUEUE_NAME, durable=True)
            self.channel.basic_qos(prefetch_count=1)
            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
            
    def ensure_connection(self):
        try:
            if not self.connection or self.connection.is_closed:
                logger.info("Reconnecting to RabbitMQ...")
                self.connect()
        except Exception as e:
            logger.error(f"Failed to reconnect: {e}")
            time.sleep(5)  # Wait before retry
            self.connect()
        
    def publish_message(self, message: dict, max_retries=3):
        for attempt in range(max_retries):
            try:
                self.ensure_connection()
                self.channel.basic_publish(
                    exchange='',
                    routing_key=Config.QUEUE_NAME,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    )
                )
                logger.info(f"Published message to queue: {message}")
                return True
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
            
    def consume_messages(self, callback):
        """Consume messages from the queue"""
        try:
            self.ensure_connection()
            self.channel.basic_consume(
                queue=Config.QUEUE_NAME,
                on_message_callback=callback,
                auto_ack=False
            )
            logger.info(f"Started consuming messages from {Config.QUEUE_NAME}")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
            raise
            
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close() 