import logging
import os
from datetime import datetime
import json

from aiogram.utils.i18n import gettext as _

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, FSInputFile

from ai.worker import ask_ai
from loader import ics_creator
from keyboards.user import user_kb
from loader import bot, db

logger = logging.getLogger(__name__)


class TaskCreation(StatesGroup):
    waiting_for_text = State()


async def start_ics_creation(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == TaskCreation.waiting_for_text.state:
        await message.answer(_("⛔️ Вы уже начали составление задачи, отправьте её."), reply_markup=user_kb)
        return
    await message.answer(
        _("Отправьте сообщение с задачами\n\n"
          "Бот извлечет суть задачи, время и место")
        )
    await state.set_state(TaskCreation.waiting_for_text)


async def create_ics_command(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get("busy"):
        await message.answer(_("⏳ Уже идёт генерация задач. Пожалуйста, дождитесь завершения."), reply_markup=user_kb)
        return
    await state.update_data(busy=True)
    try:
        text = message.text.strip()

        if len(text) < 15:
            await message.answer(_("⛔️ Слишком маленькое сообщение"), reply_markup=user_kb)
            await state.clear()
            return

        if len(text) > 750:
            await message.answer(_("⛔️ Слишком большое сообщение"), reply_markup=user_kb)
            await state.clear()
            return

        await message.answer(_("🔄 Генерация задач..."))
        await state.clear()

        try:
            logger.info(
                "Создание задачи: время=%s, юзер=%s|%s, текст=%s",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                message.from_user.id,
                message.from_user.full_name,
                text.replace("\n", ""),
                )
            resp = await ask_ai(text)
            db.add_request(
                text,
                message.from_user.id,
                json.dumps(resp, ensure_ascii=False),
                )
        except Exception as exc:
            logger.exception("Не удалось запросить AI: %s", exc)
            await message.answer(_("❌ Не удалось создать список задач:\nНет ответа"), reply_markup=user_kb)
            return

        if not resp:
            await message.answer(_("❌ Не удалось создать список задач:\nПустой ответ"), reply_markup=user_kb)
            return

        if resp.get("error"):
            extra = f" {resp['response']}" if resp.get('response') else ""
            await message.answer(
                _(f"❌ Не удалось создать список задач:\n{resp['error']}{extra}"),
                reply_markup=user_kb,
                )
            return

        if "events_tasks" not in resp:
            await message.reply(_("❌ Не удалось создать список задач:\nв JSON отсутствует поле 'events_tasks'"), reply_markup=user_kb)
            return

        await message.answer(resp.get("response", ""), reply_markup=user_kb)
        logger.debug(resp)
        event_tasks = [
            t
            for t in resp["events_tasks"]
            if t.get("type", "").strip().lower() in ["event", "task"]
            ]
        if not event_tasks:
            return
        logger.debug(event_tasks)
        settings = db.get_settings(message.from_user.id) or {}
        colors = {
            1: settings.get("color_q1"),
            2: settings.get("color_q2"),
            3: settings.get("color_q3"),
            4: settings.get("color_q4"),
            0: settings.get("color_default"),
        }
        tz = settings.get("timezone", "UTC")
        ics_filename = ics_creator.create_ics({"events_tasks": event_tasks}, tz, colors)
        if not ics_filename:
            logger.error("Не удалось создать ICS файл")
            await message.answer(
                _("❌ Не удалось сгенерировать ICS файл для переданных мероприятий"),
                reply_markup=user_kb,
                )
            return

        try:
            await send_ics_file(message.chat.id, ics_filename)
        finally:
            try:
                os.unlink(ics_filename)
            except OSError as e:
                logger.exception("Не удалось удалить временный файл %s: %s", ics_filename, e)
    finally:
        await state.update_data(busy=False)


async def send_ics_file(chat_id: int, ics_filename: str) -> None:
    """Отправить пользователю файл ICS."""
    if not os.path.exists(ics_filename):
        logger.error("Файл %s не найден", ics_filename)
        return

    try:
        await bot.send_document(chat_id, FSInputFile(ics_filename))
    except Exception as e:
        logger.exception("Ошибка отправки ICS: %s", e)
