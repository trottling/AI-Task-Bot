from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


user_kb = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text="❓ Помощь"),
        KeyboardButton(text="❇️ Создать задачи"),
        KeyboardButton(text="⚙️ Настройки"),
    ]],
    resize_keyboard=True,
)

