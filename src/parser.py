import asyncio

from loguru import logger
import requests
import bs4

from typing import List

from src.models import Game
from src.cache import add_game


TARGET_URL = "https://store.steampowered.com/search/?maxprice=free&specials=1&cc=RU"

COOKIES = {
    'steamCountry': 'RU',
    'birthtime': '0',
    'wants_mature_content': '1'
}

def process_price(price: str | None) -> int | None:
    if not price: return None
    return int(price.replace(',', '').replace(' руб', '').strip())

def process_discount(discount: str | None) -> int | None:
    if not discount: return None
    return int(discount.replace('%', '').replace('-', '').strip())

def get_name(game_element: bs4.element.PageElement) -> str:
    return game_element.find('span', class_='title').text

def get_price_data(game_element: bs4.element.PageElement):
    original_price = game_element.find('div', class_='discount_original_price').text
    current_price = game_element.find('div', class_='discount_final_price').text
    discount = game_element.find('div', class_='discount_pct').text
    return process_price(original_price), process_price(current_price), process_discount(discount)

async def get_free_games() -> List[Game]:
    result = requests.get(TARGET_URL, cookies=COOKIES)
    soup = bs4.BeautifulSoup(result.text, 'html.parser')
    games = soup.find_all('a', class_='search_result_row')
    logger.info(f"Найдено бесплатных игр: {len(games)}")
    result = []
    for game_element in games:
        name = get_name(game_element)
        game_url = game_element.get('href')
        original_price, current_price, discount = get_price_data(game_element)
        game = Game(name, original_price, current_price, discount, game_url)
        result.append(game)
    for game in result:
        await add_game(game)
    return result


if __name__ == "__main__":
    asyncio.run(get_free_games())