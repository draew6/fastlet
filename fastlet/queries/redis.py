from redis.asyncio import Redis
from ..utils.settings import get_settings

def get_activity_redis_client() -> Redis:
    settings = get_settings("bff")
    return Redis(
            username=settings.activity_redis_username,
            password=settings.activity_redis_password,
            host=settings.activity_redis_host,
            port=settings.activity_redis_port,
            decode_responses=True,
            ssl=False
    )