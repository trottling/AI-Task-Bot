from aiogram import Bot, Dispatcher

from data import config
from db.sqlite import Database

ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN

bot = Bot(TOKEN)
db = Database(path_to_db="data/main.db")
dp = Dispatcher()