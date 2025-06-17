import aioschedule as schedule

from src.parser import get_free_games
from src.cache import get_new_free_games
from src.bot import send_notifications

async def update_games_info():
    new_games = await get_free_games()
    should_notify_about = await get_new_free_games(new_games)
    await send_notifications(should_notify_about)

schedule.every().day.at("10:30").do(update_games_info)