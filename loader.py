import sys

import httpx
from aiogram import Bot, Dispatcher, Router
from openai import AsyncOpenAI

from config import config
from storage.sqlite import Database

# Bot
ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN

router = Router()
bot = Bot(TOKEN)
db = Database(path_to_db="storage/main.db")
dp = Dispatcher()

# Ai
AI_API_KEY = config.AI_API_KEY
AI_API_URL = config.AI_API_URL
AI_MODE = config.AI_MODE.lower()
PROXY_URL = config.AI_PROXY_URL

if AI_MODE not in ["chat_completions", "completions"]:
    print("AI_MODE must be either 'chat_completions' or 'completions'")
    sys.exit(1)

if not AI_API_URL:
    AI_API_URL = None
else:
    AI_API_URL = AI_API_URL.rstrip("/")
    if not AI_API_URL.endswith("/v1"):
        AI_API_URL += "/v1"

if PROXY_URL:
    http_client = httpx.AsyncClient(proxy=PROXY_URL)
    ai_client = AsyncOpenAI(
        api_key=AI_API_KEY,
        base_url=AI_API_URL,
        http_client=http_client
        )
else:
    ai_client = AsyncOpenAI(
        api_key=AI_API_KEY,
        base_url=AI_API_URL)
