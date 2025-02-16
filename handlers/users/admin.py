from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message

from filters.admin import IsAdminFilter
from keyboards.admin import admin_kb
from main import ADMINS, db, dp


@dp.message(Command("admin"), IsAdminFilter(ADMINS))
async def is_admin(message: Message):
    await message.answer(text="Админка", reply_markup=admin_kb)


@dp.message(F.text == "Стата по юзерам", IsAdminFilter(ADMINS))
async def users_count(message: Message):
    counts = db.count_users()
    text = f"В бд {counts[0]} юзеров"
    await message.answer(text=text)


@dp.message(F.text == "Стата по юзерам", IsAdminFilter(ADMINS))
async def reqs_count(message: Message):
    counts = db.count_reqs()
    text = f"В бд {counts[0]} запросов"
    await message.answer(text=text)
