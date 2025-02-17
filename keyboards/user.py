from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

user_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="⭐ Помощь"),
            KeyboardButton(text="❇️ Создать задачи"),
            KeyboardButton(text="ℹ️ О боте")
            ]
        ],
    resize_keyboard=True,
    )
