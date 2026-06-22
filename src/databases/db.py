import logging
from scraper import fetch_data
from parser.AtbParser import AtbParser
from parser.EvaParser import EvaParser
from parser.SteamParser import SteamParser
from parser.TechParser import RozetkaParser, ComfyParser
PARSERS_URL = {
	'eva.ua': EvaParser,	
	'steampowered.com': SteamParser,
	'rozetka.com': RozetkaParser,
	'atbmarket.com': AtbParser,
	'comfy.ua': ComfyParser
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
