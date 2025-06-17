import asyncio
from typing import List

import sqlite3

from src.models import Game

connection = sqlite3.connect('games.db')

async def create_schema():
    cursor = connection.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            original_price REAL,
            current_price REAL,
            discount INTEGER,
            url TEXT
        );

        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_chat_id INTEGER
        )
    """)
    connection.commit()

async def add_game(game: Game):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO games (name, original_price, current_price, discount, url) VALUES (?, ?, ?, ?, ?)",
        (game.name, game.original_price, game.current_price, game.discount, game.url)
    )
    connection.commit()

async def add_games(games: List[Game]):
    cursor = connection.cursor()
    cursor.executemany(
        "INSERT OR IGNORE INTO games (name, original_price, current_price, discount, url) VALUES (?, ?, ?, ?, ?)",
        [(game.name, game.original_price, game.current_price, game.discount, game.url) for game in games]
    )
    connection.commit()

async def get_games() -> list[Game]:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM games")
    return [Game(*row) for row in cursor.fetchall()]

async def clear_games():
    cursor = connection.cursor()
    cursor.execute("DELETE FROM games")
    connection.commit()

async def add_subscriber(telegram_chat_id: int):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO subscribers (telegram_chat_id) VALUES (?)",
        (telegram_chat_id,)
    )
    connection.commit()

async def remove_subscriber(telegram_chat_id: int):
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM subscribers WHERE telegram_chat_id = ?",
        (telegram_chat_id,)
    )
    connection.commit()

async def get_subscribers() -> list[int]:
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM subscribers")
    return [row[0] for row in cursor.fetchall()]

async def get_new_free_games(new_games: List[Game]) -> List[Game]:
    old_games = await get_games()
    result = []
    for game in new_games:
        if game.name not in [g.name for g in old_games]:
            result.append(game)
    await clear_games()
    await add_games(new_games)
    return result

if __name__ == "__main__":
    asyncio.run(create_schema())