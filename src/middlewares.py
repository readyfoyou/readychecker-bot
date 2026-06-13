from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message 
import aiosqlite
# TODO заменить проверку через aiosqlite на REDIS 
class AddPrem:
	async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:
		user_id = event.from_user.id
			
		async with aiosqlite.connect('checker_db.db') as db:
			async with db.execute('SELECT 1 FROM premium_users WHERE user_id = ?',(user_id,)) as cur:
				users_exists = await cur.fetchone()
			
			if not users_exists:
				print(f'пользователь {user_id} зашел впервые')
				await db.execute("INSERT INTO premium_users (user_id, max_prod, is_premium) VALUES (?, ?, ?)", (user_id, 5, 0))
				await db.commit()
			else: 
				print(f'пользователь {user_id} уже не впервые здесь')
		return await handler(event, data)
		
		
