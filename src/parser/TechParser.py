from parser.base import BaseParser
class RozetkaParser(BaseParser):
	async def parse(self) -> tuple:
		price_element = self.soup.find('p', class_='product-price__big')
		old_pr_el = self.soup.find('p', class_='product-price__small')
		name_el = self.soup.find("h1", class_='title__font')
		if price_element:
			price_text = price_element.text
			cl_pr = ''.join(filter(str.isdigit, price_text))
			rw_pr = int(cl_pr) if cl_pr else 0
		else:
			rw_pr = 0
		if old_pr_el:
			price_text = old_pr_el.text
			cl_old_pr = ''.join(filter(str.isdigit, price_text))
			old_price = int(cl_old_pr) if cl_old_pr else 0
			dsct = ((int(old_price) - rw_pr) / old_price) * 100
			dsc = f'{round(dsct)}%'
		else:
			old_price = 0
			dsc = 'Скидки нет'
		name = name_el.text.strip() if name_el else "Название не найдено"
		return name, rw_pr, old_price, dsc

class ComfyParser(BaseParser):
	async def parse(self) -> tuple:
		price_element = self.soup.find('div', class_='price__current')
		old_pr_el = self.soup.find('div', class_='price__old-price')
		name_el = self.soup.find("h1", class_='product-title')
		if price_element:
			price_text = price_element.text
			cl_pr = ''.join(filter(str.isdigit, price_text))
			rw_pr = int(cl_pr) if cl_pr else 0
		else:
			rw_pr = 0
		if old_pr_el:
			price_text = old_pr_el.text
			cl_old_pr = ''.join(filter(str.isdigit, price_text))
			old_price = int(cl_old_pr) if cl_old_pr else 0
			dsct = ((int(old_price) - rw_pr) / old_price) * 100
			dsc = f'{round(dsct)}%'
		else:
			old_price = 0
			dsc = "Скидки нет"
		name = name_el.text.strip() if name_el else "Название не найдено"	
		return name, rw_pr, old_price, dsc