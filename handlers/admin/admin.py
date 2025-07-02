import logging
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from keyboards.admin import admin_kb
from loader import db
from services.admin_service import AdminService

logger = logging.getLogger(__name__)

admin_service = AdminService(db)

class GrantAccess(StatesGroup):
    waiting_for_id = State()
    waiting_for_chat_id = State()

class RevokeAccess(StatesGroup):
    waiting_for_id = State()
    waiting_for_chat_id = State()

async def is_admin(message: Message) -> None:
    await message.answer(text="✅ Панель админа", reply_markup=admin_kb)

async def users_count(message: Message) -> None:
    count = admin_service.get_users_count()
    await message.answer(f"✅ В бд {count} юзеров", reply_markup=admin_kb)

async def reqs_count(message: Message) -> None:
    count = admin_service.get_reqs_count()
    await message.answer(f"✅ В бд {count} запросов", reply_markup=admin_kb)

async def allow_access_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(GrantAccess.waiting_for_id)
    await message.answer("✏️ Введите ID пользователя для выдачи доступа:", reply_markup=admin_kb)

async def allow_chat_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(GrantAccess.waiting_for_chat_id)
    await message.answer("✏️ Введите ID чата для выдачи доступа:", reply_markup=admin_kb)

async def allow_access(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Некорректный ID", reply_markup=admin_kb)
        return
    result = admin_service.set_user_access(user_id, True)
    if result["success"]:
        await message.answer(f"✅ Пользователю {user_id} выдан доступ", reply_markup=admin_kb)
    else:
        await message.answer(f"❌ Ошибка выдачи доступа: {result.get('error', '')}", reply_markup=admin_kb)

async def allow_chat(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        chat_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Некорректный ID", reply_markup=admin_kb)
        return
    result = admin_service.set_chat_access(chat_id, True)
    if result["success"]:
        await message.answer(f"✅ Чату {chat_id} выдан доступ", reply_markup=admin_kb)
    else:
        await message.answer(f"❌ Ошибка выдачи доступа чату: {result.get('error', '')}", reply_markup=admin_kb)

async def deny_access_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(RevokeAccess.waiting_for_id)
    await message.answer("✏️ Введите ID пользователя для запрета доступа:", reply_markup=admin_kb)

async def deny_chat_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(RevokeAccess.waiting_for_chat_id)
    await message.answer("✏️ Введите ID чата для запрета доступа:", reply_markup=admin_kb)

async def deny_access(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Некорректный ID", reply_markup=admin_kb)
        return
    result = admin_service.set_user_access(user_id, False)
    if result["success"]:
        await message.answer(f"✅ Пользователь {user_id} лишен доступа", reply_markup=admin_kb)
    else:
        await message.answer(f"❌ Ошибка запрета доступа: {result.get('error', '')}", reply_markup=admin_kb)

async def deny_chat(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        chat_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Некорректный ID", reply_markup=admin_kb)
        return
    result = admin_service.set_chat_access(chat_id, False)
    if result["success"]:
        await message.answer(f"✅ Чат {chat_id} лишен доступа", reply_markup=admin_kb)
    else:
        await message.answer(f"❌ Ошибка запрета доступа чату: {result.get('error', '')}", reply_markup=admin_kb)
