import logging
import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message, ReplyKeyboardMarkup, KeyboardButton

from keyboards.user import collect_kb, user_kb
from loader import bot, db, ics_creator
from services.task_service import TaskService

logger = logging.getLogger(__name__)

task_service = TaskService(db=db, ics_creator=ics_creator)

router = Router()


class TaskCreation(StatesGroup):
    collecting_tasks = State()
    generating = State()


async def start_ics_creation(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == TaskCreation.collecting_tasks.state:
        await message.answer('⛔️ Вы уже начали составление задач. Отправьте все задачи и нажмите "**Продолжить**".', reply_markup=collect_kb, parse_mode="MarkdownV2")
        return

    await state.clear()
    await state.set_state(TaskCreation.collecting_tasks)
    await state.update_data(tasks=[])
    await message.answer('✍️ Отправьте или пересылайте сообщения с задачами.\nКогда закончите — нажмите "Продолжить".\n\nℹ️ Бот понимает суть, время, место и квадрат Эйзенхауэра', reply_markup=collect_kb)


@router.message(TaskCreation.collecting_tasks, lambda m: m.text and m.text.strip() not in ["➡️ Продолжить", "❌ Отмена"])
async def collect_task_message(message: Message, state: FSMContext):
    data = await state.get_data()
    tasks = data.get("tasks", [])
    tasks.append(message.text.strip())
    await state.update_data(tasks=tasks)
    await message.answer("✅ Добавлено!\nМожете отправить ещё задачу или нажать 'Продолжить'.", reply_markup=collect_kb)


@router.message(TaskCreation.collecting_tasks, lambda m: m.text == "❌ Отмена")
async def cancel_task_collection(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Создание задач отменено.", reply_markup=user_kb)


@router.message(TaskCreation.collecting_tasks, lambda m: m.text == "➡️ Продолжить")
async def finish_task_collection(message: Message, state: FSMContext):
    data = await state.get_data()
    tasks = data.get("tasks", [])
    if not tasks:
        await message.answer("❌ Вы не отправили ни одной задачи. Отправьте хотя бы одну задачу.", reply_markup=collect_kb)
        return

    await state.set_state(TaskCreation.generating)
    await message.answer("🔄 Генерация задач...", reply_markup=user_kb)
    await state.clear()

    # Объединяем все задачи в один текст через перевод строки
    all_text = "\n".join(tasks)
    result = await task_service.process_task_text(text=all_text, user_id=message.from_user.id, chat_id=message.chat.id, message_chat_type=message.chat.type)

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
