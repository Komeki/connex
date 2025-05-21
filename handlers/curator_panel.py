from aiogram import Router, F
from aiogram.types import Message

from utils.roles import admin_required
from keyboards.inline import curator_panel_events

router = Router()

#1 Обработчик кнопок 
@router.message(F.text == "📋 Мероприятия")
@admin_required
async def show_stats(message: Message):
    await message.answer(
        "Меню мероприятий:", reply_markup=curator_panel_events()
    )

#2 Обработчик кнопок
@router.message(F.text == "📊 Аналитика")
@admin_required
async def add_event(message: Message):
    await message.answer('Еще не готово.')

#3 Обработчик кнопки
@router.message(F.text == "❌ Выход")
@admin_required
async def cancel_admin(message: Message):
    await message.answer('Еще не готово.')