from aiogram.types import Message


async def faq_command(message: Message) -> None:
    await message.answer(
        "Подробная инструкция по работе с ответами на частые вопросы:\n\n"
        "https://telegra.ph/111-07-01-32"
    )

