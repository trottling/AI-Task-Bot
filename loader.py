import httpx
from aiogram import Bot, Dispatcher, Router
from openai import AsyncOpenAI

from config import config
from storage.sqlite import Database

ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
AI_API_KEY = config.AI_API_KEY
AI_API_URL = config.AI_API_URL

if not AI_API_URL:
    AI_API_URL = None
else:
    AI_API_URL = AI_API_URL.rstrip("/")
    if not AI_API_URL.endswith("/v1"):
        AI_API_URL += "/v1"

http_client = httpx.AsyncClient()

ai_client = AsyncOpenAI(
    api_key=AI_API_KEY,
    base_url=AI_API_URL)

router = Router()
bot = Bot(TOKEN)
db = Database(path_to_db="storage/main.db")
dp = Dispatcher()
