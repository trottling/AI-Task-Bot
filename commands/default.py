from aiogram import Bot
from aiogram.methods.set_my_commands import BotCommand
from aiogram.types import BotCommandScopeDefault


async def set_default_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="/start", description="🔁 Перезапустить бота"),
        BotCommand(command="/help", description="❓ Помощь"),
        BotCommand(command="/create", description="❇️ Создать задачи"),
        BotCommand(command="/timezone", description="🌍 Установить часовой пояс (например, /timezone +3)"),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())

