from bs4 import BeautifulSoup
from parser.base import BaseParser
import re
class AtbParser(BaseParser):
	async def parse(self) -> tuple:
		price_element = self.soup.find('data', class_='product-price__top')
		old_pr_el = self.soup.find('data', class_='product-price__bottom')
		name_el = self.soup.find("h1", class_='product-page__title')
		discount = self.soup.find('span', class_='custom-product-label')
		if price_element:
			price_text = price_element.text
			del_elements = price_text.replace(' ', '')
			match = re.search(r'\d+\.?\d*', del_elements)
			if match:
				rw_pr = float(match.group())
			else:
				rw_pr = 0.0
		else:
			rw_pr = 0.0
		old_price = old_pr_el.text.strip() if old_pr_el else "Старой цены нет"
		name = name_el.text.strip() if name_el else "Название не найдено"
		dsc = discount.text.strip() if discount else "Скидки нет"
		return name, rw_pr, old_price, dsc
