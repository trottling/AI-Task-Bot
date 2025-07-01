from aiogram.types import Message


async def help_command(message: Message) -> None:
    await message.answer(
        "⭐️ Отправьте сообщение с одним или несколькими мероприятиями, например:\n\n"
        "20 января, вождение в 10 часов, с собой взять паспорт\n\n"
        "Нажмите на полученный файл и добавьте в календарь"
    )

