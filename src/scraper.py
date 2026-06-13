import asyncio
import aiohttp

async def fetch_data(url):
		
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
	}
	cookies = {
		"wants_mature_content": "1",
		"birthtime": "946684801" # 01.01.2000
	}
	async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
		
		async with session.get(url) as response:
			
			if response.status == 200:
				return await response.text()
			else:
				print("vse ploho", response.status_code)
				return None
