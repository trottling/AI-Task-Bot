from aiogram import Bot, Dispatcher, Router
from openai import AsyncOpenAI

from data import config
from db.sqlite import Database

ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
AI_API_KEY = config.AI_API_KEY
AI_API_URL = config.AI_API_URL

if AI_API_URL == "":
    AI_API_URL = None

ai_client = AsyncOpenAI(api_key=AI_API_KEY, base_url=AI_API_URL)
router = Router()
bot = Bot(TOKEN)
db = Database(path_to_db="data/main.db")
dp = Dispatcher()
