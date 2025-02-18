import json

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from ai_utils.worker import ask_ai
from ics_util.generator import generate_ics
from loader import bot

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
        resp = await ask_ai(text)
    except Exception as e:
        print(e)
        await message.answer("❌ Не удалось создать список задач: Нет ответа")
        return

    if resp == "":
        await message.answer("❌ Не удалось создать список задач: Пустой ответ")

    try:
        resp = json.loads(resp)
    except Exception as e:
        print(e)
        await message.answer("❌ Не удалось создать список задач: Ошибка загрузки JSON")
        return

    if resp["error"] == "":
        await message.answer(f"❌ Не удалось создать список задач: {resp['error']}")
        return

    if "events_tasks" not in resp:
        await message.reply("❌ Не удалось создать список задач: в JSON отсутствует поле 'events_tasks'")
        return

    await message.answer(resp["response"])

    for event_task in resp["events_tasks"]:
        ics_cal = generate_ics(event_task)
        await message.answer(resp["answer"] + ":")
        await send_ics(message.chat.id, ics_cal)


async def send_ics(chat_id, ics_cal):
    await bot.send_document(chat_id, ics_cal)
