from aiogram import Dispatcher, F
from aiogram.filters import Command

from filters.admin import IsAdminFilter
from filters.access import HasAccessFilter
from loader import db, router
from . import users
from . import admin
from .users.ics import TaskCreation, router as ics_router


async def register_handlers(dp: Dispatcher, admins: list[int]) -> None:
    # Команды без состояния
    dp.message.register(users.start.start_command, Command("start"))
    dp.message.register(admin.admin.is_admin, Command("admin"), IsAdminFilter(admins))
    dp.message.register(users.help.help_command, Command("help"))

    access_filter = HasAccessFilter(admins, db)

    dp.message.register(users.start.help_command, F.text == "❓ Помощь", access_filter)

    # FSM-настройки
    router.message.register(users.settings.settings_command, F.text == "⚙️ Настройки", access_filter)

    # FSM создание задач
    router.message.register(users.ics.start_ics_creation, F.text == "❇️ Создать задачи", access_filter)
    dp.message.register(users.ics.create_from_reply, Command("create"), access_filter)

    dp.include_router(router)
    dp.include_router(ics_router)

    # Админ
    dp.message.register(admin.admin.users_count, F.text == "🔢 Стата по юзерам", IsAdminFilter(admins))
    dp.message.register(admin.admin.reqs_count, F.text == "🔢 Стата по запросам", IsAdminFilter(admins))
    dp.message.register(users.start.start_command, F.text == "◀️ Назад", IsAdminFilter(admins))

    dp.message.register(admin.admin.allow_access_prompt, F.text == "🟢 Дать доступ юзеру", IsAdminFilter(admins))
    router.message.register(admin.admin.allow_access, admin.admin.GrantAccess.waiting_for_id, IsAdminFilter(admins))
    dp.message.register(admin.admin.deny_access_prompt, F.text == "🔴 Убрать доступ юзеру", IsAdminFilter(admins))
    router.message.register(admin.admin.deny_access, admin.admin.RevokeAccess.waiting_for_id, IsAdminFilter(admins))
    dp.message.register(admin.admin.allow_chat_prompt, F.text == "🟢 Дать доступ чату", IsAdminFilter(admins))
    router.message.register(admin.admin.allow_chat, admin.admin.GrantAccess.waiting_for_chat_id, IsAdminFilter(admins))
    dp.message.register(admin.admin.deny_chat_prompt, F.text == "🔴 Убрать доступ чату", IsAdminFilter(admins))
    router.message.register(admin.admin.deny_chat, admin.admin.RevokeAccess.waiting_for_chat_id, IsAdminFilter(admins))
