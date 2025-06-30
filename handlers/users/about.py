from aiogram.types import Message


async def about_command(message: Message):
    await message.answer(
        "ℹ️ Бот преобразует текст в задачи и выдаёт ссылки на Google, Яндекс и Mail.ru календари"
    )
