import redis.asyncio as aioredis
from redis.asyncio import Redis
import logging
from app.core.config import config

class AsyncRedisClient:
    _client: Redis = None

    @classmethod
    async def initialize(cls) -> Redis:
        """
        Инициализирует Redis-клиент, если это еще не сделано.
        """
        if cls._client is None:
            cls._client = await aioredis.from_url(
                config.celery.CELERY_BROKER_URL,
                max_connections=30,
                encoding="utf8",
                decode_responses=True,
                socket_connect_timeout=15,
                socket_timeout=15,
            )
            logging.info("AsyncRedisClient is initialized.")
        return cls._client

    @classmethod
    async def get_client(cls) -> Redis:
        """
        Возвращает инстанс Redis клиента. Если клиент не инициализирован, инициализирует его.
        """
        return await cls.initialize()

# Функция для использования Redis клиента в FastAPI через Depends
async def get_redis_client() -> Redis:
    """
    Зависимость для FastAPI: возвращает Redis клиент через Depends.
    """
    client = await AsyncRedisClient.get_client()
    logging.info("AsyncRedisClient is being used in a FastAPI request.")
    return client
