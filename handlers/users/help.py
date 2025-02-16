from aiogram.types import Message
from main import dp
from aiogram.filters import Command


#help commands
@dp.message(Command("help"))
async def help_commands(message:Message):
    await message.answer("Отправьте сообщение с одним или несколькими мероприятиями, например:\n\n20 января, вождение в 10 часов, с собой взять паспорт\n\nНажмите на полученный файл и добавьте в календарь")
