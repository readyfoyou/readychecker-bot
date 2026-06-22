from redis.asyncio import Redis
from typing import Optional, Any
class RedisCache:
    def __init__(self, redis_url: str, cache_ttl: Optional[int] = None):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.cache_ttl = cache_ttl
    
    async def get(self, key: str):
        return await self.redis.get(key)

    async def set(self, key: str, value: Any):
        await self.redis.set(key, value, ex=self.cache_ttl)

    async def delete(self, key: str):
        await self.redis.delete(key)

    