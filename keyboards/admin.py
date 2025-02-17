from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Стата по юзерам"),
            KeyboardButton(text="Стата по запросам"),
            KeyboardButton(text="Назад")
            ]

        ],
    resize_keyboard=True,
    )
