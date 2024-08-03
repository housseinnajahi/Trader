import json
from typing import Optional

import redis

from .settings.redis_settings import redis_settings


class RedisClient:
    def __init__(self, db: int = 0):
        self.redis_conn = redis.StrictRedis(
            host=redis_settings.REDIS_HOST,
            port=redis_settings.REDIS_PORT,
            db=db,
            decode_responses=True,
        )

    def get(self, key: str) -> Optional[str]:
        value = self.redis_conn.get(key)
        return value if value else None

    def set(self, key: str, value: str, ttl: Optional[int] = None):
        if ttl:
            self.redis_conn.set(key, value, ex=ttl)
        else:
            self.redis_conn.set(key, value)

    def delete(self, key: str):
        return self.redis_conn.delete(key)

    def add_to_list(self, key: str, element: str):
        self.redis_conn.rpush(key, element)

    def get_list_elements(self, key: str, start: int = 0, end: int = -1):
        return self.redis_conn.lrange(key, start, end)

    def get_computed_aggregations(self, key: str = "computed_aggregations") -> dict:
        computed_aggregations = self.redis_conn.get(key)
        return json.loads(computed_aggregations)

    def set_computed_aggregations(
        self, key: str = "computed_aggregations", computed_aggregations: dict = {}
    ):
        computed_aggregations_str = json.dumps(computed_aggregations)
        self.redis_conn.set(key, computed_aggregations_str)

    def publish_message(self, data: dict, channel: str = "GENERATE_PREDICTION"):
        message = json.dumps(data)
        self.redis_conn.publish(channel, message)
        return {"status": f"Message published to generate prediction for {data['ticker']}"}


redis_client = RedisClient()


def redis_subscriber(channel: str = "GENERATE_PREDICTION"):
    pubsub = redis_client.redis_conn.pubsub()
    pubsub.subscribe(channel)
    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            print(f"Received message: {data}")
