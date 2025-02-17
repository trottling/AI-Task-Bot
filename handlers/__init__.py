from aiogram import Dispatcher, F
from aiogram.filters import Command

from filters.admin import IsAdminFilter
from . import users


async def register_handlers(dp: Dispatcher, ADMINS):
    dp.message.register(users.start.start_command, Command("start"))

    dp.message.register(users.help.help_command, Command("help"))

    dp.message.register(users.about.about_command, Command("about"))

    dp.message.register(users.create_ics.create_ics_command)

    dp.message.register(users.admin.is_admin, Command("admin"), IsAdminFilter(ADMINS))
    dp.message.register(users.admin.users_count, F.Text("Стата по юзерам"), IsAdminFilter(ADMINS))
    dp.message.register(users.admin.users_count, F.Text("Стата по запросам"), IsAdminFilter(ADMINS))
