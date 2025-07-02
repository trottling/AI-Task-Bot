import logging
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from loader import _

from keyboards.admin import admin_kb
from loader import db

logger = logging.getLogger(__name__)


class GrantAccess(StatesGroup):
    waiting_for_id = State()
    waiting_for_chat_id = State()


class RevokeAccess(StatesGroup):
    waiting_for_id = State()
    waiting_for_chat_id = State()

async def is_admin(message: Message) -> None:
    await message.answer(text=_("✅ Админка"), reply_markup=admin_kb)


async def users_count(message: Message) -> None:
    counts = db.count_users()
    await message.answer(_("✅ В бд {count} юзеров").format(count=counts[0]))


async def reqs_count(message: Message) -> None:
    counts = db.count_reqs()
    await message.answer(_("✅ В бд {count} запросов").format(count=counts[0]))


async def allow_access_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(GrantAccess.waiting_for_id)
    await message.answer(_("Введите ID пользователя для выдачи доступа:"))


async def allow_chat_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(GrantAccess.waiting_for_chat_id)
    await message.answer(_("Введите ID чата для выдачи доступа:"))


async def allow_access(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer(_("❌ Некорректный ID"))
        return
    try:
        db.set_access(user_id, True)
        await message.answer(_("Пользователю {user_id} выдан доступ").format(user_id=user_id))
    except Exception as exc:
        logger.exception("Не удалось выдать доступ: %s", exc)
        await message.answer(_("❌ Ошибка выдачи доступа"))


async def allow_chat(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        chat_id = int(message.text.strip())
    except ValueError:
        await message.answer(_("❌ Некорректный ID"))
        return
    try:
        db.set_chat_access(chat_id, True)
        await message.answer(_("Чату {chat_id} выдан доступ").format(chat_id=chat_id))
    except Exception as exc:
        logger.exception("Не удалось выдать доступ чату: %s", exc)
        await message.answer(_("❌ Ошибка выдачи доступа чату"))


async def deny_access_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(RevokeAccess.waiting_for_id)
    await message.answer(_("Введите ID пользователя для запрета доступа:"))


async def deny_chat_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(RevokeAccess.waiting_for_chat_id)
    await message.answer(_("Введите ID чата для запрета доступа:"))


async def deny_access(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer(_("❌ Некорректный ID"))
        return
    try:
        db.set_access(user_id, False)
        await message.answer(_("Пользователь {user_id} лишен доступа").format(user_id=user_id))
    except Exception as exc:
        logger.exception("Не удалось запретить доступ: %s", exc)
        await message.answer(_("❌ Ошибка запрета доступа"))


async def deny_chat(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        chat_id = int(message.text.strip())
    except ValueError:
        await message.answer(_("❌ Некорректный ID"))
        return
    try:
        db.set_chat_access(chat_id, False)
        await message.answer(_("Чат {chat_id} лишен доступа").format(chat_id=chat_id))
    except Exception as exc:
        logger.exception("Не удалось запретить доступ чату: %s", exc)
        await message.answer(_("❌ Ошибка запрета доступа чату"))
