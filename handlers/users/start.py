from aiogram.types import Message

from loader import db


async def start_command(message: Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name, telegram_id=telegram_id)
        await message.answer(text=f"👋 Привет, {full_name}, нажми /help что бы понять как работает бот")
    except:
        pass
