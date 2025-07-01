from aiogram.types import Message


async def help_command(message: Message) -> None:
    await message.answer(
        "ℹ️ Бот создаёт задачи для календаря из сообщения\n\n"
        "1) Отправляете боту сообщение с задачей, например:\n"
        "20 января, вождение в 10 часов, с собой взять паспорт\n\n"
        "2) Открываете файлы, которые прислал бот и добавляете мероприятия в любой календарь - на Android, IPhone или ПК"
        )
