import os

from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import BufferedInputFile, Message

from loguru import logger
from dotenv import load_dotenv

from src.parser import get_free_games
from src.models import Game

load_dotenv()

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
        "Подробнее о боте можно узнать в разделе README.md на [GitHub](https://github.com/f0rgenet/discount-steam-bot/README.md)",
        parse_mode="Markdown"
    )

@dp.message(Command("free"))
async def free(message: Message):
    logger.info(f"Пользователь {message.from_user.username} начал поиск скидок в Steam...")
    await message.reply("Поиск скидок в Steam...")
    games: list[Game] = get_free_games()
    
    if not games:
        await message.reply("К сожалению, сейчас нет бесплатных игр или скидок не найдено.")
        logger.info(f"Для пользователя {message.from_user.username} не найдено скидок.")
        return

    result_message_parts = ["Вот список бесплатных игр и игр со скидками в Steam:\n"]
    for game in games:
        game_info = (
            f"<b>{game.name}</b>\n"
            f"<s>{game.original_price} ₽</s> {game.current_price} ₽\n"
            f"Скидка {game.discount}%\n"
            f"<a href='{game.url}'>Забрать</a>\n"
        )
        result_message_parts.append(game_info)
    
    full_result_message = "\n".join(result_message_parts)
    await message.reply(full_result_message, parse_mode="html")
    logger.success(f"Пользователь {message.from_user.username} завершил поиск скидок в Steam!")

async def run():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(e)
    finally:
        dp.shutdown()
