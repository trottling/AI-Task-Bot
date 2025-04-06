from aiogram.types import Message
import json
import os

from ai_utils.worker import ask_ai

from ics_util.generator import generate_ics
from loader import bot


async def create_ics_command(message: Message):
    await message.answer("Отправьте сообщение с задачами:")
    text = message.text

    if len(text) < 10:
        await message.answer("Слишком маленькое сообщение")
        return

    if len(text) > 500:
        await message.answer("Слишком большое сообщение")
        return

    await message.answer("🔄 Генерация ивента...")

    try:
        resp = await ask_ai(text)
    except Exception as e:
        print(e)
        await message.answer("❌ Не удалось создать список задач: Нет ответа")
        return

    if resp == "":
        await message.answer("❌ Не удалось создать список задач: Пустой ответ")
        return

    try:
        resp = json.loads(resp)
    except Exception as e:
        print(e)
        await message.answer("❌ Не удалось создать список задач: Ошибка загрузки JSON")
        return

    if resp.get("error"):
        await message.answer(f"❌ Не удалось создать список задач: {resp['error']}")
        return

    if "events_tasks" not in resp:
        await message.reply("❌ Не удалось создать список задач: в JSON отсутствует поле 'events_tasks'")
        return

    await message.answer(resp.get("response", ""))

    for event_task in resp["events_tasks"]:
        ics_filename = generate_ics(event_task)
        if not ics_filename:
            await message.answer("❌ Не удалось сгенерировать ICS файл для одной из задач")
            continue
            
        try:
            await send_ics_file(message.chat.id, ics_filename)
        finally:
            # Clean up temporary file
            try:
                os.unlink(ics_filename)
            except:
                pass


async def send_ics_file(chat_id, ics_filename):
    with open(ics_filename, "rb") as file:
        await bot.send_document(chat_id, file)
