import asyncio
import logging
import random
import aiosqlite
from dotenv import load_dotenv
import os
from aiogram import Router, html, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from databases.db import get_all_data
load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID"))

router = Router() 

class UrlAdd(StatesGroup):
	ssilka = State()
	waiting_fo_back = State()
	waiting_fo_report = State()

class AdminReply(StatesGroup):
	waiting_for_reply = State()

kb1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Добавить товар", callback_data='addthis')], 
    [InlineKeyboardButton(text="🗒 Помощь", callback_data="help"), InlineKeyboardButton(text="🗂 Список товаров", callback_data="catalog")],
	[InlineKeyboardButton(text="📨 Сообщить о проблеме", callback_data="report")]
])

kback = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='◀️ ️Вернуться назад', callback_data='go_back')]
])

kb_for_check = InlineKeyboardMarkup(inline_keyboard=[
	[InlineKeyboardButton(text='◀️ ️Вернуться назад', callback_data='back_n_delete')]
])

async def check_all_prod(bot: Bot):
	logging.info('Начало проверки')
	async with aiosqlite.connect('checker_db.db') as db:
		async with db.execute('SELECT user_id, product_name, current_price, discount, old_price, ssilka FROM user_products') as cur:
			all_products = await cur.fetchall()
	
	if not all_products:
		logging.info('Нет данных')
		return 
	
	for row in all_products:
		user_id, old_name, db_price, db_discount, db_old_price, url = row

		try:
			#name, price, old_price, discount #TODO поменять названия на нормальные
			i1, i2, i3, i4 = await get_all_data(url)
			
			if db_price > i2:
				await bot.send_message(chat_id=user_id, text=f'''
				🚨Появилась скидка на ваш товар!
📦 Название: {i1}
💰 Новая цена: {i2}₴
📉 Скидка: {i4}
🏪 Старая цена: {i3}
👜 Предыдущая цена в боте: {db_price}₴

🔗 [Перейти к товару]({url})

Если вы считаете что произошла ошибка(например html товара не был найдет, или бот выдает неккоректную ссылку, напишите в предложку)
			''', parse_mode="Markdown")
			
			async with aiosqlite.connect("checker_db.db") as db_upd:
				await db_upd.execute('UPDATE user_products SET current_price = ?, old_price = ?, product_name = ?, discount = ? WHERE user_id = ? AND ssilka = ?',
					(i2, i3, i1, i4, user_id, url)
				)
				await db_upd.commit()
			await asyncio.sleep(1.5)
		except Exception as e:
			logging.error(f"Ошибка при автоматической проверке товара {url} для пользователя {user_id}: {e}")
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {message.from_user.full_name}! С помощью этого бота ты сможешь отслеживать скидки, и текущую стоимость выбранных товаров. На данный момент присутствует поддержка таких сервисов: Eva, Steam, ATB, Silpo, Rozetka. Приятного пользования!", 
        reply_markup=kb1
    )

@router.callback_query(F.data == 'addthis')
async def add_urls(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UrlAdd.ssilka)
    await callback.answer()
    await callback.message.edit_text("Скиньте мне ссылку на товар, и я добавлю его в ваш каталог.")

@router.message(UrlAdd.ssilka, F.text.regexp(r'^https?://[^\s]+$'))
async def add_urls_second(message: Message, state: FSMContext):
	user_id = message.from_user.id
    
	async with aiosqlite.connect('checker_db.db') as db:
		async with db.execute('SELECT COUNT(*) FROM user_products WHERE user_id = ?', (user_id,)) as cursor:
			count = await cursor.fetchone()
			current_count = count[0] if count else 0
			
		async with db.execute('SELECT max_prod FROM premium_users WHERE user_id = ?', (user_id,)) as cur:
			max_prod = await cur.fetchone()	
	if current_count >= max_prod[0]:
		await message.answer(f'Лимит добавленных товаров достигнут!({max_prod[0]}) Чтобы добавить еще один товар, удалите один из добавленных раньше', reply_markup=kback)
		await state.clear()
		return
	else:
		#name, price, old_price, discount #TODO поменять названия на нормальные
		i1, i2, i3, i4 = await get_all_data(message.text)
		await message.answer(f'''✅ Ссылка была успешно добавлена! Вот данные про ваш текущий товар: 
📦Название: {i1} 
💰Текущая цена: {i2}₴
📉Скидка: {i4} 
🏪Старая цена: {i3}''', reply_markup=kback)
        
		async with aiosqlite.connect('checker_db.db') as db:
			await db.execute(
                'INSERT INTO user_products (user_id, ssilka, current_price, old_price, product_name, discount) VALUES (?, ?, ?, ?, ?, ?)', 
                (user_id, message.text, i2, i3, i1, i4)
            )
			await db.commit()
		await state.clear() 

@router.message(UrlAdd.ssilka)
async def add_urls_invalid(message: Message):
    await message.answer("👀 Ой, это не похоже на ссылку! Пожалуйста, отправь корректный URL-адрес (он должен начинаться с http:// или https://).")

@router.callback_query(F.data == 'go_back')
async def go_back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text=f"Привет, {callback.from_user.full_name}! С помощью этого бота ты сможешь отслеживать скидки, и текущую стоимость выбранных товаров. На данный момент присутствует поддержка таких сервисов: Eva, Steam, ATB, Silpo, Rozetka.Приятного пользования!",
        reply_markup=kb1
    ) 
    
@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
	user_id = callback.from_user.id
	async with aiosqlite.connect('checker_db.db') as db:
		async with db.execute('SELECT rowid, product_name, current_price, discount, old_price, ssilka FROM user_products WHERE user_id = ?', (user_id,)) as cursor:
			temp_data = await cursor.fetchall() 
		await callback.answer()	
		
		if not temp_data:
			await callback.message.edit_text("🗓 Ваш каталог пока пуст. Нажмите «Добавить товар», чтобы начать отслеживание!", reply_markup=kback)
			return
		
		kb = InlineKeyboardBuilder()
		
		for row in temp_data:
			product_id = row[0]
			product_name = row[1]
			
			shrt_name = product_name[:35] + '...' if len(product_name) > 35 else product_name
			
			kb.add(InlineKeyboardButton(text=shrt_name, callback_data=f'tovar_{product_id}'))
		kb.add(InlineKeyboardButton(text='◀️ ️Вернуться назад', callback_data='go_back'))
		kb.adjust(1)
		
		await callback.message.edit_text('🗓 Вот ваши текущие товары (нажмите на товар для подробностей): ', reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith('tovar_'))
async def show_product_details(callback: CallbackQuery):
	product_id = int(callback.data.split('_')[1])
	async with aiosqlite.connect('checker_db.db') as db:
		async with db.execute('SELECT product_name, current_price, discount, old_price, ssilka FROM user_products WHERE rowid = ?', (product_id,)) as cursor:
			product = await cursor.fetchone()
	await callback.answer()
	if not product:
		await callback.message.edit_text('❌ Товар не найден в базе данных.', reply_markup=kback)
		return
	name, cur_price, discount, old_price, url = product
	text = (
		f"📦 *{name}*\n\n"
		f"💰 *Текущая цена:* {cur_price}₴\n"
		f"📉 *Скидка:* {discount}\n"
		f"🏪 *Старая цена:* {old_price if old_price else '—'}\n"
	)
	kb = InlineKeyboardBuilder()
	kb.add(InlineKeyboardButton(text='🔗 Перейти к товару', url=url))
	kb.add(InlineKeyboardButton(text='🗑 Удалить из каталога', callback_data=f'delete_{product_id}'))
	kb.add(InlineKeyboardButton(text='◀️ Назад в каталог', callback_data='catalog'))
	kb.adjust(1)
	await callback.message.edit_text(
        text=text, 
        reply_markup=kb.as_markup(), 
        parse_mode="Markdown"
    )
@router.callback_query(F.data.startswith('delete_'))
async def delete_product(callback: CallbackQuery):
    product_id = int(callback.data.split('_')[1])
    async with aiosqlite.connect('checker_db.db') as db:
        await db.execute('DELETE FROM user_products WHERE rowid = ?', (product_id,))
        await db.commit()
    await callback.answer("Товар удален из отслеживания", show_alert=False)
    await callback.message.edit_text(
        text="✅ Товар был успешно удален из вашего каталога.", 
        reply_markup=kback 
    )

@router.callback_query(F.data == 'help')
async def helping_msg(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Этот бот умеет отслеживать скидки на выбранные вами товары. Для того чтобы начать им пользоваться, нажмите кнопку "Добавить товар", после чего выполните инструкции бота. Приятного пользования!', reply_markup=kback)

@router.callback_query(F.data == 'report')
async def report(callback: CallbackQuery, state: FSMContext):
	await state.set_state(UrlAdd.waiting_fo_report)
	await callback.answer()
	await callback.message.edit_text("Пожалуйста, опишите проблему, с которой вы столкнулись. Мы постараемся помочь вам как можно скорее.", reply_markup=kback)

@router.message(UrlAdd.waiting_fo_report)
async def handle_report(message: Message, state: FSMContext, bot: Bot):
	await state.clear()
	user_id = message.from_user.id
	user_username = message.from_user.username
	report_text = message.text

	kb_report = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="💬 Ответить пользователю",callback_data=f"reply_{user_id}")]
	])

	await bot.send_message(
		chat_id=ADMIN_ID, 
		text=f"📬 <b>Новое обращение</b>\n\n"
            f"👤 От: {user_username}"
            f"🆔 User ID: <code>{user_id}</code>\n\n"
            f"💬 <b>Сообщение:</b>\n{message.text}",
		parse_mode="HTML",
		reply_markup=kb_report
	)

	logging.info(f"Пользователь {user_id} отправил отчет: {report_text}")
	
	await message.answer("Спасибо за ваш отчет! Мы рассмотрим вашу проблему и постараемся помочь вам как можно скорее.", reply_markup=kback)
	await state.clear()

@router.callback_query(F.data.startswith('reply_'))
async def reply_to_user(callback: CallbackQuery, state: FSMContext):
	if callback.from_user.id != ADMIN_ID: 
		await callback.answer("У вас нет прав для ответа на это сообщение.", show_alert=True)
		return
	
	target_user_id = int(callback.data.split("_")[1])
	await state.update_data(target_user_id=target_user_id)
	await state.set_state(AdminReply.waiting_for_reply)
 
	await callback.answer()
	await callback.message.answer(
    	f"✍️ Введи ответ для пользователя <code>{target_user_id}</code>:",
    	parse_mode="HTML"
    )

@router.message(AdminReply.waiting_for_reply)
async def send_reply_to_user(message: Message, state: FSMContext, bot: Bot):
	if message.from_user.id != ADMIN_ID:
		await message.answer("У вас нет прав для отправки этого сообщения.")
		return
	
	data = await state.get_data()
	target_user_id = data.get("target_user_id")
	await state.clear()

	try:
		await bot.send_message(
			chat_id=target_user_id,
			text=f"💬 <b>Ответ от администрации:</b>\n\n{message.text}",
			parse_mode="HTML"
		)
		await message.answer(f"✅ Ответ успешно отправлен пользователю <code>{target_user_id}</code>.", parse_mode="HTML")
	except Exception as e:
		logging.error(f"Ошибка при отправке ответа пользователю {target_user_id}: {e}")
		await message.answer(f"❌ Не удалось отправить сообщение пользователю <code>{target_user_id}</code>. Возможно, пользователь заблокировал бота или произошла другая ошибка.", parse_mode="HTML")

''' кнопка 'Проверить сейчас' удалена по причине поломки логики бота'''
# @router.callback_query(F.data == 'check_now')    
# async def check_now(callback: CallbackQuery, state: FSMContext):
# 	user_id = callback.from_user.id
# 	async with aiosqlite.connect('checker_db.db') as db:
# 		async with db.execute('SELECT product_name, current_price, discount, old_price, ssilka FROM user_products WHERE user_id = ?', (user_id,)) as cursor:
# 			product = await cursor.fetchall()
# 	if not product:
# 		await callback.message.edit_text('❌ Товар не найден в базе данных.', reply_markup=kback)
# 		return
# 	await callback.answer()
# 	msgs = []
	
# 	msgs.append(callback.message.message_id)
	
# 	for row in product:
# 		i1, i2, i3, i4 = await get_all_data(row[4])
# 		if row[1] > i2:
# 			msg = await callback.message.answer(f'''Скидка на товар появилась! Вот данные про ваш текущий товар: 
# 📦Название: {i1} 
# 💰Текущая цена: {i2}₴ 
# 📉Скидка: {i4} 
# 🏪Старая цена: {i3}
# 👜Цена до проверки: {row[1]}''')
# 			msgs.append(msg.message_id)
# 		else: 
# 			msg = await callback.message.answer(f'''Скидка на товар не появилась! Вот данные про ваш текущий товар:
# 📦Название: {i1} 
# 💰Текущая цена: {i2}₴ 
# 📉Скидка: {i4}
# 🏪Старая цена: {i3}
# 👜Цена до проверки: {row[1]}''')
# 			msgs.append(msg.message_id)
# 	last_msg = await callback.message.answer(f'Вернуться назад', reply_markup=kb_for_check)
# 	msgs.append(last_msg.message_id)
# 	await state.update_data(messages_to_delete=msgs)
# 	await state.set_state(UrlAdd.waiting_fo_back)
	
# @router.callback_query(F.data == 'back_n_delete', UrlAdd.waiting_fo_back)
# async def back_n_delete(callback: CallbackQuery, state: FSMContext, bot: Bot):
# 		user_data = await state.get_data()
# 		messages_to_delete = user_data.get("messages_to_delete", [])
# 		if messages_to_delete:
# 			try:
# 				await bot.delete_messages(
# 					chat_id=callback.message.chat.id,
# 					message_ids=messages_to_delete
# 				)
# 			except Exception as e:
# 				logging.error(f"Ошибка при удалении сообщений: {e}")
		
# 		await callback.message.answer(
# 			text=f"Привет, {callback.from_user.full_name}! С помощью этого бота ты сможешь отслеживать скидки, и текущую стоимость выбранных товаров. На данный момент присутствует поддержка таких сервисов: Eva, Steam, ATB, Silpo, Rozetka. Приятного пользования!",
# 			reply_markup=kb1
# 		)
		
# 		await state.clear()
