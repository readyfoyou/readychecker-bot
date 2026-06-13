from scraper import fetch_data
from parser.EvaParser import EvaParser
from parser.SteamParser import SteamParser
from parser.RozetkaParser import RozetkaParser
PARSERS_URL = {
	'eva.ua': EvaParser,	
	'steampowered.com': SteamParser,
	'rozetka.com': RozetkaParser
}
async def get_all_data(url):
	data = await fetch_data(url)
	if not data:
		return "нет html", 0, "нет данных", "нет скидки"
	chosen_parser = None
	for domain, parser_class in PARSERS_URL.items():
		if domain in url.lower():
			chosen_parser = parser_class
			break
	if chosen_parser:
		parser = chosen_parser(data)
		name, price, old_price, discount = await parser.parse()
		return name, price, old_price, discount
	else:
		return "Сайт не поддерживается", 0, "нет данных", "0%"
