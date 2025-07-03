import logging
import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message

from keyboards.user import user_kb
from loader import bot, db, ics_creator
from services.task_service import TaskService

logger = logging.getLogger(__name__)

task_service = TaskService(db=db, ics_creator=ics_creator)

router = Router()


class TaskCreation(StatesGroup):
    waiting_for_text = State()


async def start_ics_creation(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == TaskCreation.waiting_for_text.state:
        await message.answer("⛔️ Вы уже начали составление задачи, отправьте её.", reply_markup=user_kb)
        return

    await message.answer("✍️ Отправьте сообщение с задачами\n\nℹ️ Бот понимает *суть, время, место и квадрат Эйзенхауэра*", parse_mode="MarkdownV2")
    await state.set_state(TaskCreation.waiting_for_text)


async def create_ics_command(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get("busy"):
        await message.answer("⏳ Уже идёт генерация задач. *Пожалуйста, дождитесь завершения.*", reply_markup=user_kb, parse_mode="MarkdownV2")
        return

    await state.update_data(busy=True)
    try:
        await message.answer("🔄 Генерация задач...")
        await state.clear()

        result = await task_service.process_task_text(text=message.text.strip(), user_id=message.from_user.id, chat_id=message.chat.id, message_chat_type=message.chat.type)
        if not result.get("success"):
            await message.answer(result["message"], reply_markup=user_kb, parse_mode="MarkdownV2")
            return

        await message.answer(result["message"], reply_markup=user_kb, parse_mode="MarkdownV2")

        event_tasks = result.get("event_tasks")
        if not event_tasks:
            return

        ics_filename = task_service.generate_ics(event_tasks)
        if not ics_filename:
            logger.error("Не удалось создать ICS файл")
            await message.answer("❌ Не удалось сгенерировать ICS файл для переданных мероприятий", reply_markup=user_kb, parse_mode="MarkdownV2")
            return

        try:
            await send_ics_file(message.chat.id, ics_filename)
        finally:
            try:
                os.unlink(ics_filename)
            except OSError as e:
                logger.exception(f"Не удалось удалить временный файл {ics_filename}: {e}")

    finally:
        await state.update_data(busy=False)


async def send_ics_file(chat_id: int, ics_filename: str) -> None:
    """Отправить пользователю файл ICS."""
    if not os.path.exists(ics_filename):
        logger.error(f"Файл {ics_filename} не найден")
        return

    try:
        await bot.send_document(chat_id, FSInputFile(ics_filename))
    except Exception as e:
        logger.exception(f"Ошибка отправки ICS: {e}")


@router.message(Command("create"))
async def create_from_reply(message: Message):
    if message.chat.type == "private":
        await message.answer("ℹ️ Используйте **/create** в групповых чатах в ответ на сообщение", parse_mode="MarkdownV2")
        return

    if not message.reply_to_message or not message.reply_to_message.text:
        await message.answer("ℹ️ Используйте **/create** в ответ на сообщение с задачей.", parse_mode="MarkdownV2")
        return

    if message.from_user.username == bot.username:
        await message.answer("❌ Нельзя создать задачу на сообщение бота")
        return

    await message.answer("🔄 Генерация задач...")

    result = await task_service.process_task_text(text=message.reply_to_message.text.strip(), user_id=message.from_user.id, chat_id=message.chat.id, message_chat_type=message.chat.type)
    if not result.get("success"):
        await message.answer(result["message"])
        return

    await message.answer(result["message"])

    event_tasks = result.get("event_tasks")
    if not event_tasks:
        return

    ics_filename = task_service.generate_ics(event_tasks)
    if not ics_filename:
        logger.error("Не удалось создать ICS файл")
        await message.answer("❌ Не удалось сгенерировать ICS файл для переданных мероприятий")
        return

    try:
        await send_ics_file(message.chat.id, ics_filename)
    finally:
        try:
            os.unlink(ics_filename)
        except OSError as e:
            logger.exception(f"Не удалось удалить временный файл {ics_filename}: {e}")
