from aiogram.types import Message


async def about_command(message: Message) -> None:
    await message.answer(
        "ℹ️ Бот для получения .isc файлов мероприятий для календаря из текста"
    )

