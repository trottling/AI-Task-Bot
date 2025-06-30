import logging
import os
from datetime import datetime
import json

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, FSInputFile

from ai.worker import ask_ai
from ics_util.generator import generate_ics
from keyboards.user import user_kb
from loader import bot, db

logger = logging.getLogger(__name__)


class TaskCreation(StatesGroup):
    waiting_for_text = State()


async def start_ics_creation(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == TaskCreation.waiting_for_text.state:
        await message.answer("Вы уже создаёте задачи. Пожалуйста, завершите предыдущий ввод.", reply_markup=user_kb)
        return
    await message.answer("Отправьте сообщение с задачами:")
    await state.set_state(TaskCreation.waiting_for_text)


async def create_ics_command(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("busy"):
        await message.answer("⏳ Уже идёт генерация задач. Пожалуйста, дождитесь завершения.", reply_markup=user_kb)
        return
    await state.update_data(busy=True)
    try:
        text = message.text.strip()

        if len(text) < 10:
            await message.answer("Слишком маленькое сообщение", reply_markup=user_kb)
            return

        if len(text) > 500:
            await message.answer("Слишком большое сообщение", reply_markup=user_kb)
            return

        await message.answer("🔄 Генерация задач...")
        await state.clear()

        try:
            logger.info(
                f"Создание задачи: время={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, "
                f"юзер={message.from_user.id}|{message.from_user.full_name}, текст={text}"
                )
            resp = await ask_ai(text)
            db.add_request(text, message.from_user.id, json.dumps(resp, ensure_ascii=False))
        except Exception:
            logger.exception("AI request failed")
            await message.answer("❌ Не удалось создать список задач:\nНет ответа", reply_markup=user_kb)
            return

        if not resp:
            await message.answer("❌ Не удалось создать список задач:\nПустой ответ", reply_markup=user_kb)
            return

        if resp.get("error"):
            extra = f" {resp['response']}" if resp.get('response') else ""
            await message.answer(
                f"❌ Не удалось создать список задач:\n{resp['error']}{extra}",
                reply_markup=user_kb,
                )
            return

        if "events_tasks" not in resp:
            await message.reply("❌ Не удалось создать список задач:\nв JSON отсутствует поле 'events_tasks'", reply_markup=user_kb)
            return

        await message.answer(resp.get("response", ""), reply_markup=user_kb)

        event_tasks = [t for t in resp["events_tasks"] if t.get("type", "").strip().lower() == "event"]
        if not event_tasks:
            return

        ics_filename = generate_ics(event_tasks)
        if not ics_filename:
            logger.error("Failed to generate ICS file")
            await message.answer(
                "❌ Не удалось сгенерировать ICS файл для переданных мероприятий",
                reply_markup=user_kb,
                )
            return

        try:
            await send_ics_file(message.chat.id, ics_filename)
        finally:
            try:
                os.unlink(ics_filename)
            except OSError:
                logger.exception("Failed to remove temp file %s", ics_filename)
    finally:
        await state.update_data(busy=False)


async def send_ics_file(chat_id, ics_filename):
    file = FSInputFile(ics_filename)
    await bot.send_document(chat_id, file)
