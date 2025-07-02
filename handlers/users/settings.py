import logging
import re
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton


from keyboards.user import user_kb
from loader import db

COLOR_PATTERN = r"^#[0-9a-fA-F]{6}$"

logger = logging.getLogger(__name__)


class Setup(StatesGroup):
    choosing_option = State()
    waiting_for_timezone = State()
    waiting_for_quadrant = State()
    waiting_for_color = State()


def settings_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Часовой пояс")],
            [KeyboardButton(text="Квадрат эйзенхауэра")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
    )


def timezone_kb() -> ReplyKeyboardMarkup:
    offsets = [f"{i:+d}" for i in range(-12, 15)]
    buttons = [KeyboardButton(text=o) for o in offsets]
    rows = [buttons[i:i + 4] for i in range(0, len(buttons), 4)]
    rows.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def quadrant_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1"), KeyboardButton(text="2")],
            [KeyboardButton(text="3"), KeyboardButton(text="4")],
            [KeyboardButton(text="0")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
    )


def colors_kb() -> ReplyKeyboardMarkup:
    presets = ["#ff8c00", "#ff0000", "#00ff00", "#0000ff", "#808080"]
    buttons = [KeyboardButton(text=c) for c in presets]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    rows.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


async def settings_command(message: Message, state: FSMContext) -> None:
    await message.answer("Выберите настройку", reply_markup=settings_menu_kb())
    await state.set_state(Setup.choosing_option)


async def choose_option(message: Message, state: FSMContext) -> None:
    text = message.text.lower()
    if "час" in text:
        await message.answer("Выберите часовой пояс", reply_markup=timezone_kb())
        await state.set_state(Setup.waiting_for_timezone)
        return
    if "квадрат" in text:
        await message.answer("Выберите часть", reply_markup=quadrant_kb())
        await state.set_state(Setup.waiting_for_quadrant)
        return
    if "назад" in text:
        await state.clear()
        await message.answer("Настройки сохранены", reply_markup=user_kb)
        return
    await message.answer("Выберите настройку", reply_markup=settings_menu_kb())


async def set_timezone(message: Message, state: FSMContext) -> None:
    if message.text.lower().startswith("назад"):
        await settings_command(message, state)
        return
    if not re.match(r"^[+-]?\d+$", message.text.strip()):
        await message.answer("Выберите часовой пояс", reply_markup=timezone_kb())
        return
    offset = int(message.text.strip())
    tz = f"UTC{offset:+d}"
    db.set_settings(message.from_user.id, timezone=tz)
    await message.answer("Настройки сохранены", reply_markup=settings_menu_kb())
    await state.set_state(Setup.choosing_option)


async def choose_quadrant(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if text.lower().startswith("назад"):
        await settings_command(message, state)
        return
    if text not in {"0", "1", "2", "3", "4"}:
        await message.answer("Выберите часть", reply_markup=quadrant_kb())
        return
    await state.update_data(quadrant=int(text))
    await message.answer("Выберите цвет", reply_markup=colors_kb())
    await state.set_state(Setup.waiting_for_color)


async def set_color(message: Message, state: FSMContext) -> None:
    if message.text.lower().startswith("назад"):
        await message.answer("Выберите часть", reply_markup=quadrant_kb())
        await state.set_state(Setup.waiting_for_quadrant)
        return
    color = message.text.strip()
    if not re.match(COLOR_PATTERN, color):
        await message.answer("Введите цвет в HEX", reply_markup=colors_kb())
        return
    data = await state.get_data()
    q = data.get("quadrant", 0)
    settings = db.get_settings(message.from_user.id) or {}
    colors = [
        settings.get("color_q1", "#ff8c00"),
        settings.get("color_q2", "#ff0000"),
        settings.get("color_q3", "#00ff00"),
        settings.get("color_q4", "#0000ff"),
        settings.get("color_default", "#808080"),
    ]
    idx = 4 if q == 0 else q - 1
    colors[idx] = color
    db.set_settings(message.from_user.id, colors=tuple(colors))
    await message.answer("Настройки сохранены", reply_markup=quadrant_kb())
    await state.set_state(Setup.waiting_for_quadrant)
