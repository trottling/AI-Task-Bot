from aiogram import Bot
from aiogram.methods.set_my_commands import BotCommand
from aiogram.types import BotCommandScopeDefault


async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="🔁 Перезапустить бота"),
        BotCommand(command="/help", description="⭐ Помощь"),
        BotCommand(command="/about", description="ℹ️ О боте"),

        ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
