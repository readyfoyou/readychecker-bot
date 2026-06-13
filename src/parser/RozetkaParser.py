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
		else:
			old_price = 0
		name = name_el.text.strip() if name_el else "Название не найдено"
		dsct = ((int(old_price) - rw_pr) / old_price) * 100
		dsc = f'{round(dsct)}%'
		if dsc: 
			pass
		else: 
			dsc = "Скидки нет"
		return name, rw_pr, old_price, dsc
