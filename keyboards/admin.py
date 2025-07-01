from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Стата по юзерам"), KeyboardButton(text="Стата по запросам")],
        [KeyboardButton(text="Дать доступ"), KeyboardButton(text="Убрать доступ")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
)

