import logging
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message 
from databases.redis_module import RedisCache
import aiosqlite
'''Требуется проверить есть ли данные в Redis(конкретно is_premium), если данных нет, то создать подключение к бд, дать ответ
и записать данные в Redis, если данные есть, то просто взять их оттуда и дать овтет, не подключаясь к бд'''
class AddPrem(BaseMiddleware):
	def __init__(self, redis_cache: RedisCache):
		super().__init__()
		self.redis_cache = redis_cache
	
	async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:
		user_id = event.from_user.id
		is_premium = await self.redis_cache.get(f"user:{user_id}:is_premium")
		if is_premium is not None:
			return await handler(event, data)
		else:
			async with aiosqlite.connect('checker_db.db') as db:
				async with db.execute('SELECT is_premium FROM premium_users WHERE user_id = ?',(user_id,)) as cur:
					result = await cur.fetchone()
					if result is not None:
						is_premium = result[0]
						await self.redis_cache.set(f"user:{user_id}:is_premium", is_premium)
					else:
						await db.execute("INSERT INTO premium_users (user_id, max_prod, is_premium) VALUES (?, ?, ?)", (user_id, 5, 0))
						await db.commit()
						await self.redis_cache.set(f"user:{user_id}:is_premium", 0)
		return await handler(event, data)
		
		
