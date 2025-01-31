# parser.py
import requests
from bs4 import BeautifulSoup

class ItmoParser:
    """
    Парсим пока одну базовую ссылочку
    """
    def __init__(self, base_url: str = "https://itmo.ru/ru/"):
        self.base_url = base_url

    def fetch_main_page_text(self) -> str:
        response = requests.get(self.base_url)
        if response.status_code != 200:
            return ""
        soup = BeautifulSoup(response.text, "html.parser")
        # текст всех тегов <p>
        paragraphs = soup.find_all("p")
        text_data = "\n".join(p.get_text() for p in paragraphs)
        return text_data

    def parse_additional_page(self, url: str) -> str:
        # и аналогично для других страниц
        response = requests.get(url)
        if response.status_code != 200:
            return ""
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text_data = "\n".join(p.get_text() for p in paragraphs)
        return text_data

    def gather_all_texts(self, url_list: list) -> list:
        contents = []
        for url in url_list:
            text = self.parse_additional_page(url)
            contents.append(text)
        return contents