# import time
# import redis
# import logging
# import os
# # redis_client = redis.Redis(host='redis', port=6379, decode_responses=True, socket_timeout=2)
# redis_client = redis.Redis(host='localhost', port=7000, decode_responses=True, socket_timeout=2)

# # redis_host = os.getenv("REDIS_HOST", "localhost")
# # redis_port = int(os.getenv('REDIS_PORT', 6379))
# # Initialize the Redis client
# # redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
# def check_redis_health():
  
#     try:
#         # Ping Redis server to check if it's up
#         response = redis_client.ping()
#         if response:
#             logging.info("Redis is up and running!")
#             return True
#     except redis.ConnectionError as e:
#         logging.error(f"Redis connection error: {e}")
#     except Exception as e:
#         logging.error(f"Unexpected error when checking Redis health: {e}")
        
#     return False

# # Call this function to check Redis status
# if check_redis_health():
#     print("Redis is running.")
# else:
#     print("Redis is not available.")


from redis import Redis
from loguru import logger

from app.core.configs.config import get_settings

config = get_settings()

try:
    redis_client = Redis(
        host=config.REDIS_URL,
        port=config.REDIS_PORT,
        charset="utf-8",
        decode_responses=True
    )
    logger.info("Redis Client Created")

except Exception as e:
    logger.error(f"Redis Client Creation Failed: {e}")
    redis_client = None


@logger.catch
def get_redis_client():
    return redis_client