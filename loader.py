import httpx
from aiogram import Bot, Dispatcher, Router
from aiogram.utils.i18n import SimpleI18nMiddleware

from utils.txt_i18n import TxtI18n
from openai import AsyncOpenAI

from config import config
from ics.creator import ICSCreator
from storage.sqlite import Database

# Bot
ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN

router = Router()
bot = Bot(TOKEN)
db = Database(path_to_db="storage/main.db")
dp = Dispatcher()
ics_creator = ICSCreator()

# I18n
i18n = TxtI18n(path="locales", default_locale="ru", domain="bot")
_ = i18n.gettext


class DBI18nMiddleware(SimpleI18nMiddleware):
    async def get_locale(self, event, data):
        user = data.get("event_from_user")
        if user:
            settings = db.get_settings(user.id)
            if settings and settings.get("language"):
                return settings["language"]
        return await super().get_locale(event, data)

dp.message.middleware.register(DBI18nMiddleware(i18n))
dp.callback_query.middleware.register(DBI18nMiddleware(i18n))

# Ai
AI_API_KEY = config.AI_API_KEY
AI_API_URL = config.AI_API_URL
PROXY_URL = config.AI_PROXY_URL

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
