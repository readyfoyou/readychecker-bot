from bs4 import BeautifulSoup

class BaseParser:
	def __init__(self, pg: str):
		self.soup = BeautifulSoup(pg, 'lxml')
    
	async def parse(self) -> tuple:
		raise NotImplementedError('не прописан парсер')
