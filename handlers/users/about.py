from aiogram.types import Message
from main import dp
from aiogram.filters import Command


# about commands
@dp.message(Command("about"))
async def about_commands(message: Message):
    await message.answer("Бот для получения .isc файлов мероприятий для календаря из текста")
