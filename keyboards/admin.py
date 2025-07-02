from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔢 Стата по юзерам"), KeyboardButton(text="🔢 Стата по запросам")],
        [KeyboardButton(text="🟢 Дать доступ юзеру"), KeyboardButton(text="🔴 Убрать доступ юзеру")],
        [KeyboardButton(text="🟢 Дать доступ чату"), KeyboardButton(text="🔴 Убрать доступ чату")],
        [KeyboardButton(text="◀️ Назад")],
    ],
    resize_keyboard=True,
)

