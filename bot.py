import logging

from aiogram import Bot, Dispatcher

from main import ADMINS, dp


@dp.startup()
async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin), text="Бот запущен")
        except Exception as err:
            logging.exception(err)


@dp.shutdown()
async def off_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin), text="Бот отключен")
        except Exception as err:
            logging.exception(err)
