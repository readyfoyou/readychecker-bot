import asyncio
from curl_cffi.requests import AsyncSession

async def fetch_data(url):
    cookies = {
        "wants_mature_content": "1",
        "birthtime": "946684801" # 01.01.2000
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }

    async with AsyncSession() as session:
        try:
            response = await session.get(
                url,
                cookies=cookies,
                headers=headers,
                impersonate='chrome120',
                timeout=10
            )
            if response.status_code == 200:
                if "Pardon Our Interruption" in response.text:
                    print("Ой-ой, сайт(возможно комфи) выдал страницу блокировки (капчу)!")
                    return None
                return response.text
            else:
                print("Ошибка парсинга:", response.status_code)
                return None
        except Exception as e:
            print('Ошибка при запросе:', e)
            return None