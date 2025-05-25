from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards.fabrics import event_list_kb, Pagination
from keyboards.student_reply import student_main_kb
from utils.roles import user
from utils.database import (
    get_user_registrations,
    calculate_user_activity,
    get_user_profile,
    get_available_events
)

router = Router()

# /menu
@router.message(Command("menu"))
@user
async def student_menu(message: Message):
    await message.answer(
        "<b>Панель студента</b>\nВыберите действие:",
        reply_markup=student_main_kb,
        parse_mode="HTML"
    )

# reply кнопка мероприятия
@router.message(F.text == "📅 Мероприятия")
async def show_events(message: Message):
    events = get_available_events()
    if not events:
        await message.answer("🎉 На данный момент нет доступных мероприятий.")
        return
    
    await message.answer(
        "📋 Доступные мероприятия:",
        reply_markup=event_list_kb(page=0)
    )

# Обработка пагинации (общая для всех)
@router.callback_query(Pagination.filter())
async def paginate_events(callback: CallbackQuery, callback_data: Pagination):
    await callback.answer()
    await callback.message.edit_reply_markup(
        reply_markup=event_list_kb(page=callback_data.page)
    )

@router.message(F.text == "📝 Мои регистрации")
@user
async def show_my_registrations(message: Message):
    registrations = get_user_registrations(message.from_user.id)
    
    if not registrations:
        await message.answer("🗂 Вы не зарегистрированы ни на одно мероприятие.")
        return
    
    response = ["<b>🗂 Ваши регистрации:</b>\n"]
    for reg in registrations:
        status = "✅ Посещено" if reg['attended'] else "🕒 Запланировано"
        response.append(
            f"\n<b>🔥 {reg['event_name']}</b>\n"
        )
    
    await message.answer("\n".join(response), parse_mode="HTML")

@router.message(F.text == "📈 Моя активность")
@user
async def show_my_activity(message: Message):
    stats = calculate_user_activity(message.from_user.id)
    
    response = (
        "<b>📊 Ваша активность:</b>\n\n"
        f"🔹 Посещено мероприятий: {stats['attended_count']}\n"
        f"🔹 Запланировано: {stats['missed_count']}\n"
        f"🔹 Процент посещаемости: {stats['attendance_rate']}%\n"
        f"🔹 Всего баллов: {stats['total_points']}\n\n"
        f"<i>100 баллов за каждое посещенное мероприятие</i>"
    )
    
    await message.answer(response, parse_mode="HTML")

@router.message(F.text == "👤 Профиль")
@user
async def show_profile(message: Message):
    profile = get_user_profile(message.from_user.id)
    stats = calculate_user_activity(message.from_user.id)
    telegram = message.from_user.username
    response = (
        f"<b>👤 Ваш профиль</b> — @{telegram}\n\n"
        f"🔹 <b>ФИО:</b> {profile['full_name']}\n"
        f"🔹 <b>Курс:</b> {profile['course']}\n"
        f"🔹 <b>Направление:</b> {profile['major']}\n"
        f"🔹 <b>Группа:</b> {profile['group_num']}\n"
        f"🔹 <b>Дата регистрации:</b> {profile['registration_date']}\n\n"
        f"<b>Активность:</b>\n"
        f"• Посещено мероприятий: {stats['attended_count']}\n"
        f"• Всего баллов: {stats['total_points']}"
    )
    
    await message.answer(response, parse_mode="HTML")