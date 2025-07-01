from aiogram import Dispatcher, F
from aiogram.filters import Command

from filters.admin import IsAdminFilter
from filters.access import HasAccessFilter
from loader import db, router
from . import users
from .users.ics import TaskCreation


async def register_handlers(dp: Dispatcher, admins: list[int]) -> None:
    dp.message.register(users.start.start_command, Command("start"))
    dp.message.register(users.admin.is_admin, Command("admin"), IsAdminFilter(admins))

    access_filter = HasAccessFilter(admins, db)

    dp.message.register(users.help.help_command, F.text == "⭐ Помощь", access_filter)
    dp.message.register(users.about.about_command, F.text == "ℹ️ О боте", access_filter)

    router.message.register(
        users.ics.start_ics_creation,
        F.text == "❇️ Создать задачи",
        access_filter,
    )
    router.message.register(
        users.ics.create_ics_command,
        TaskCreation.waiting_for_text,
        access_filter,
    )
    dp.include_router(router)

    dp.message.register(users.admin.users_count, F.text == "Стата по юзерам", IsAdminFilter(admins))
    dp.message.register(users.admin.reqs_count, F.text == "Стата по запросам", IsAdminFilter(admins))
    dp.message.register(users.start.start_command, F.text == "Назад", IsAdminFilter(admins))

    dp.message.register(users.admin.allow_access_prompt, F.text == "Дать доступ", IsAdminFilter(admins))
    router.message.register(users.admin.allow_access, users.admin.GrantAccess.waiting_for_id, IsAdminFilter(admins))
    dp.message.register(users.admin.deny_access_prompt, F.text == "Убрать доступ", IsAdminFilter(admins))
    router.message.register(users.admin.deny_access, users.admin.RevokeAccess.waiting_for_id, IsAdminFilter(admins))

