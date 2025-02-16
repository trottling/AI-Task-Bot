from aiogram.types import Message

from keyboards.admin import admin_kb
from loader import db


async def is_admin(message: Message):
    await message.answer(text="Админка", reply_markup=admin_kb)


async def users_count(message: Message):
    counts = db.count_users()
    await message.answer(f"В бд {counts[0]} юзеров")


async def reqs_count(message: Message):
    counts = db.count_reqs()
    await message.answer(f"В бд {counts[0]} запросов")
