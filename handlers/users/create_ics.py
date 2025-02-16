from aiogram.types import Message

async def create_ics_command(message: Message):
    if message.text in ["/start", "/help", "/about"]:
        return

    if len(message.text) < 10:
        await message.answer("Слишком маленькое сообщение")
        return

    if len(message.text) > 500:
        await message.answer("Слишком большое сообщение")
        return

    await message.answer("Отправьте сообщение с одним или несколькими мероприятиями, например:\n\n20 января, вождение в 10 часов, с собой взять паспорт\n\nНажмите на полученный файл и добавьте в календарь")
