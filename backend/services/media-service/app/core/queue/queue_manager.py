# app/core/queue/queue_manager.py
from aio_pika import connect_robust, Message
import json
from loguru import logger

class QueueManager:
    def __init__(self):
        self.rabbitmq_url = "amqp://guest:guest@localhost/"

    async def publish(self, queue_name: str, data: dict):
        try:
            connection = await connect_robust(self.rabbitmq_url)
            channel = await connection.channel()
            
            queue = await channel.declare_queue(queue_name, durable=True)
            
            message = Message(
                json.dumps(data).encode(),
                delivery_mode=2
            )
            
            await channel.default_exchange.publish(message, routing_key=queue_name)
            await connection.close()
            logger.info(f"Message published to queue {queue_name}")
        except Exception as e:
            logger.error(f"Failed to publish message to queue: {str(e)}")
            raise

queue_manager = QueueManager()