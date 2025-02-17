from aiogram import Bot, Dispatcher
from openai import AsyncOpenAI

from data import config
from db.sqlite import Database

ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
DEEPSEEK_KEY = config.DEEPSEEK_KEY

ai_client = AsyncOpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
bot = Bot(TOKEN)
db = Database(path_to_db="data/main.db")
dp = Dispatcher()
