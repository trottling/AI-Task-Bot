from aiogram import Dispatcher, F
from aiogram.filters import Command

from filters.admin import IsAdminFilter
from loader import router
from . import users
from .users.ics import TaskCreation


async def register_handlers(dp: Dispatcher, ADMINS):
    dp.message.register(users.start.start_command, Command("start"))
    dp.message.register(users.admin.is_admin, Command("admin"), IsAdminFilter(ADMINS))

    dp.message.register(users.help.help_command, F.text == "⭐ Помощь")
    dp.message.register(users.about.about_command, F.text == "ℹ️ О боте")

    router.message.register(users.ics.start_ics_creation, F.text == "❇️ Создать задачи")

    router.message.register(users.ics.create_ics_command, TaskCreation.waiting_for_text)
    dp.include_router(router)

    dp.message.register(users.admin.users_count, F.text == "Стата по юзерам", IsAdminFilter(ADMINS))
    dp.message.register(users.admin.reqs_count, F.text == "Стата по запросам", IsAdminFilter(ADMINS))
    dp.message.register(users.start.start_command, F.text == "Назад", IsAdminFilter(ADMINS))
