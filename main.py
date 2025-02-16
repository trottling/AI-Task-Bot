import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from commands.default import set_default_commands
from data import config
from db.sqlite import Database
from aiogram.enums import ParseMode

ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN

bot = Bot(TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
db = Database(path_to_db="data/main.db")
dp = Dispatcher()


async def main() -> None:
    await set_default_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())
