from bs4 import BeautifulSoup
from parser.base import BaseParser

class SteamParser(BaseParser):
	async def parse(self) -> tuple:
		name_el = self.soup.find(id='appHubAppName') or self.soup.find("div", class_='apphub_AppName')
		name = name_el.text.strip() if name_el else "Название не найдено"
		
		price_element = None
		old_pr_el = None
		discount = None

		discount_block = self.soup.find('div', class_='discount_block')
		if discount_block:
			price_element = discount_block.find('div', class_='discount_final_price')
			old_pr_el = discount_block.find('div', class_='discount_original_price')
			discount = discount_block.find('div', class_='discount_pct')

		if not price_element:
			price_element = self.soup.find('div', class_='game_purchase_price')
			if not price_element:
				price_element = self.soup.find('div', class_='price')

			old_price = "Старой цены нет"
			dsc = "Скидки нет"
		else:
			old_price = old_pr_el.text.strip() if old_pr_el else "Старой цены нет"
			dsc = discount.text.strip() if discount else "Скидки нет"

		if price_element:
			price_text = price_element.text.strip()
			if any(word in price_text.lower() for word in ["free", "бесплатно", "безкоштовно"]):
				rw_pr = 0
				old_price = "Бесплатно"
			else:
				cl_pr = ''.join(filter(str.isdigit, price_text))
				rw_pr = int(cl_pr) if cl_pr else 0
		else:
			rw_pr = 0
		return name, rw_pr, old_price, dsc
