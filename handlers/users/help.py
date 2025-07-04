from aiogram.types import Message


async def help_command(message: Message) -> None:
    await message.answer(
        "ℹ️ Бот создаёт задачи для календаря из сообщения\n\n"
        "1) Отправляете боту сообщение с задачей, например:\n"
        "20 января, вождение в 10 часов, с собой взять паспорт\n\n"
        "Для создания задач в чате используйте команду /create\n\n"
        "2) Открываете файл, который прислал бот и добавляете мероприятия в любой календарь - на Android, IPhone или ПК\n\n"
        "Подробная инструкция по работе с ответами на частые вопросы:\nhttps://telegra.ph/FAQ--CHasto-zadavaemye-voprosy-po-AI-Task-Bot-07-03"
        )
