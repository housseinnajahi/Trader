import json
from typing import Optional

import redis
from .lstm import generate_prediction

from .settings.redis_settings import redis_settings


class RedisClient:
    def __init__(self, db: int = 0):
        self.redis_conn = redis.StrictRedis(
            host=redis_settings.REDIS_HOST,
            port=redis_settings.REDIS_PORT,
            db=db,
            decode_responses=True,
        )

    def publish_message(self, data: dict, channel: str = "GENERATE_PREDICTION"):
        message = json.dumps(data)
        self.redis_conn.publish(channel, message)
        return {"status": "Message published"}


redis_client = RedisClient()


def redis_subscriber(channel: str = "GENERATE_PREDICTION"):
    pubsub = redis_client.redis_conn.pubsub()
    pubsub.subscribe(channel)
    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            print(f"Received message: {data}")
            generate_prediction(data=data)
