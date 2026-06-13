import asyncio
import logging
import aiosqlite
from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, html
from notifier import router, check_all_prod
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from middlewares import AddPrem
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
	
async def init_db():
	async with aiosqlite.connect("checker_db.db") as db:
		await db.execute('''
			CREATE TABLE IF NOT EXISTS user_products (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_id INTEGER,
				ssilka TEXT,
				current_price REAL DEFAULT 0.0,
				old_price REAL DEFAULT 0.0,
				product_name TEXT, 
				discount INTEGER
			)
		''')
		await db.execute('''
			CREATE TABLE IF NOT EXISTS premium_users (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_id INTEGER,
				max_prod INTEGER,
				is_premium INTEGER
			)
		''')
		await db.commit()

async def main():
	scheduler = AsyncIOScheduler()
	scheduler.add_job(check_all_prod, "interval", minutes=30, kwargs={"bot": bot})
	scheduler.start()
	logging.info("Планировщик успешно запущен!")
	dp.message.middleware(AddPrem())
	dp.include_router(router)
	await init_db()
	try:
		await dp.start_polling(bot)
	finally:
		scheduler.shutdown()
if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("exit")
