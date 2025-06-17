import os
from typing import List

from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import BufferedInputFile, Message

from loguru import logger
from dotenv import load_dotenv

from src.parser import get_free_games
from src.models import Game
from src.cache import get_subscribers, add_subscriber

load_dotenv()

def get_games_message(games: List[Game]):
    if not games:
        return "На данный момент нет бесплатных игр по скидкам :<"
    result_message_parts = ["Вот список бесплатных игр в Steam:\n"]
    for game in games:
        game_info = (
            f"<b>{game.name}</b>\n"
            f"<s>{game.original_price} ₽</s> {game.current_price} ₽\n"
            f"Скидка {game.discount}%\n"
            f"<a href='{game.url}'>Забрать</a>\n"
        )
        result_message_parts.append(game_info)
    
    full_result_message = "\n".join(result_message_parts)
    return full_result_message

bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])

def on_startup():
    logger.success("Бот запущен!")

def on_shutdown():
    logger.info("Бот остановлен!")

dp = Dispatcher()
dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

@dp.message(Command("start"))
async def start(message: Message):
    logger.info(f"Пользователь {message.from_user.username} запустил бота!")
    await message.reply(
        "Для поиска скидок используйте `/free`\n" \
        "Подробнее о боте можно узнать в [GitHub](https://github.com/F0rgenet/discount-steam-bot/)",
        parse_mode="Markdown"
    )

@dp.message(Command("free"))
async def free(message: Message):
    logger.info(f"Пользователь {message.from_user.username} начал поиск скидок в Steam...")
    await message.reply("Поиск скидок в Steam...")
    games: list[Game] = await get_free_games()
    
    await message.reply(get_games_message(games), parse_mode="html")
    logger.success(f"Пользователь {message.from_user.username} завершил поиск скидок в Steam!")


@dp.message(Command("subscribe"))
async def subscribe(message: Message):
    if message.from_user.id in await get_subscribers():
        await message.reply("Вы уже подписаны на уведомления о скидках!")
        return
    await add_subscriber(message.from_user.id)
    await message.reply("Вы успешно подписаны на уведомления о скидках!")

async def send_notifications(games: List[Game]):
    for subscriber in await get_subscribers():
        await bot.send_message(subscriber, get_games_message(games))

async def run():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(e)
    finally:
        dp.shutdown()
