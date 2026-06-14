import asyncio
from curl_cffi.requests import AsyncSession

async def fetch_data(url):
	cookies = {
		"wants_mature_content": "1",
		"birthtime": "946684801" # 01.01.2000
	}
	async with AsyncSession() as session:
		try:
			
			response = await session.get(url, cookies=cookies, impersonate='chrome', timeout=10)

			if response.status_code == 200:
				return response.text
			else:
				print("Ошибка парсинга:", response.status_code)
				return None
		except Exception as e:
			print('Ошибка при запросе')
			return None