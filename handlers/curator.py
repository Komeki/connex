from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.admin_utils import load_admins, save_admins

router = Router()

# Загружаем список админов в память
ADMINS = load_admins()

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# Команда для добавления себя в админы
@router.message(Command("make_admin"))
async def make_admin(message: Message):
    user_id = message.from_user.id
    await message.delete()
    if user_id in ADMINS:
        await message.answer("✅ Вы уже админ.")
    else:
        ADMINS.add(user_id)
        save_admins(ADMINS)
        await message.answer("🔐 Вы добавлены в список админов.")

# Админ-панель
@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return

    await message.answer(
        "<b>Добро пожаловать в админ-панель.</b>\nВыберите действие:",
        reply_markup=admin_keyboard,
        parse_mode="HTML"
    )

# Обработка кнопок
@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery):
    await callback.message.answer("📊 Статистика ещё не реализована.")

@router.callback_query(F.data == "admin_add_event")
async def add_event(callback: CallbackQuery):
    await callback.message.answer("➕ Добавление события ещё не реализовано.")
