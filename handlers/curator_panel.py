from aiogram import Router, F
from aiogram.types import Message

from utils.admin_utils import load_admins
from keyboards.inline import curator_panel_events

router = Router()

# Загружаем список админов в память
ADMINS = load_admins()

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

#1 Обработчик кнопок 
@router.message(F.text == "📋 Мероприятия")
async def show_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "Меню мероприятий:", reply_markup=curator_panel_events()
    )

#2 Обработчик кнопок
@router.message(F.text == "📊 Аналитика")
async def add_event(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer('Еще не готово.')

#3 Обработчик кнопки
@router.message(F.text == "❌ Выход")
async def cancel_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    # Скрываем клавиатуру
    await message.answer('Еще не готово.')