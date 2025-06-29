import logging
import os

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from ai_utils.worker import ask_ai
from ics_util.generator import generate_ics
from loader import bot

logger = logging.getLogger(__name__)

class TaskCreation(StatesGroup):
    waiting_for_text = State()

async def start_ics_creation(message: Message, state: FSMContext):
    await message.answer("Отправьте сообщение с задачами:")
    await state.set_state(TaskCreation.waiting_for_text)

async def create_ics_command(message: Message, state: FSMContext):
    text = message.text.strip()

    if len(text) < 10:
        await message.answer("Слишком маленькое сообщение")
        return

    if len(text) > 500:
        await message.answer("Слишком большое сообщение")
        return

    await message.answer("🔄 Генерация ивента...")
    await state.clear()

    try:
        resp = await ask_ai(text, message.from_user.id)
    except Exception:
        logger.exception("AI request failed")
        await message.answer("❌ Не удалось создать список задач: Нет ответа")
        return

    if not resp:
        await message.answer("❌ Не удалось создать список задач: Пустой ответ")
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
            logger.error("Failed to generate ICS file for task: %s", event_task)
            await message.answer("❌ Не удалось сгенерировать ICS файл для одной из задач")
            continue
            
        try:
            await send_ics_file(message.chat.id, ics_filename)
        finally:
            try:
                os.unlink(ics_filename)
            except OSError:
                logger.exception("Failed to remove temp file %s", ics_filename)


async def send_ics_file(chat_id, ics_filename):
    with open(ics_filename, "rb") as file:
        await bot.send_document(chat_id, file)
