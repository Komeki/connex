from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject

from utils.admin_utils import load_admins, save_admins

from keyboards.curator_reply import admin_kb
from keyboards.inline import curator_panel_events

router = Router()

# Загружаем список админов в память
ADMINS = load_admins()

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# /make_admin
@router.message(Command("make_admin"))
async def make_admin(message: Message, command: CommandObject):
    user_id = message.from_user.id
    args = command.args  # Извлекаем аргументы после команды

    await message.delete()

    if args != '119':
        await message.answer("⛔ Неверный код доступа.")
        return

    if user_id in ADMINS:
        await message.answer("✅ Вы уже админ.")
    else:
        ADMINS.add(user_id)
        save_admins(ADMINS)
        await message.answer("🔐 Вы добавлены в список админов.")

# Команда /admin - reply-клавиатура
@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return

    await message.answer(
        "<b>Добро пожаловать в админ-панель.</b>\n"
        "Выберите действие с помощью кнопок ниже:",
        reply_markup=admin_kb,
        parse_mode="HTML"
    )
