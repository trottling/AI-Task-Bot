from aiogram.types import Message

from deepseek.worker import ask_ai


async def create_ics_command(message: Message):
    if len(message.text) < 10:
        await message.answer("Слишком маленькое сообщение")
        return

    if len(message.text) > 500:
        await message.answer("Слишком большое сообщение")
        return

    await message.answer("🔄 Генерация ивента...")

    resp = await ask_ai(message.text)

    await message.answer()
