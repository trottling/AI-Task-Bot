from aiogram.types import Message


async def help_command(message: Message):
    await message.answer("Отправьте сообщение с одним или несколькими мероприятиями, например:\n\n20 января, вождение в 10 часов, с собой взять паспорт\n\nНажмите на полученный файл и добавьте в календарь")
