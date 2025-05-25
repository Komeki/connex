from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from utils.states import Mailing

from keyboards.inline import filters_menu_kb
from keyboards.fabrics import course_select_post_kb, major_select_post_kb, confirm_mailing_kb, register_button

from utils.database import get_event_by_id, get_users_by_filters, is_user_registered, register_user_for_event

router = Router()

@router.callback_query(F.data == "start_mailing", Mailing.filter_select)
async def go_to_filters(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    event_id = data.get('event_id')
    event = get_event_by_id(event_id=event_id)
    await callback.message.answer(
        f"Выбранный пост: {event['name']}\n\n"
        "🔧 Выберите фильтры для рассылки:", 
        reply_markup=filters_menu_kb())

    await state.set_state(Mailing.filter_values)

@router.callback_query(F.data == "filter_course", Mailing.filter_values)
async def filters_selecting(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text('Выберите курс: ', reply_markup=course_select_post_kb())

@router.callback_query(F.data == "filter_major", Mailing.filter_values)
async def filters_selecting(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text('Выберите направление: ', reply_markup=major_select_post_kb())

@router.callback_query(F.data.startswith("course_"), Mailing.filter_values)
async def filters_selecting(callback: CallbackQuery, state: FSMContext):
    # Получаем выбранный курс
    course = callback.data.split("_")[1]
    
    # Получаем текущие фильтры
    data = await state.get_data()
    filters = data.get('filters', {})
    
    # Инициализируем список курсов если нужно
    if 'courses' not in filters:
        filters['courses'] = []
    
    # Проверяем, есть ли курс уже в фильтрах
    if course in filters['courses']:
        # Удаляем курс если он уже был выбран
        filters['courses'].remove(course)
        await callback.answer(f"Курс {course} удалён", show_alert=False)
    else:
        # Добавляем курс если его ещё нет
        filters['courses'].append(course)
        await callback.answer(f"Курс {course} добавлен", show_alert=False)
    
    # Обновляем состояние
    await state.update_data(filters=filters)
    
    # Формируем текст текущих фильтров
    filter_text = "Выбранные курсы: " + ", ".join(filters['courses']) if filters.get('courses') else "Фильтры не выбраны"
    
    # Редактируем сообщение, сохраняя клавиатуру
    await callback.message.edit_text(
        text=filter_text,
        reply_markup=course_select_post_kb()  # Оставляем ту же клавиатуру курсов
    )

@router.callback_query(F.data.startswith("major_"), Mailing.filter_values)
async def majors_selecting(callback: CallbackQuery, state: FSMContext):
    # Получаем выбранный курс
    major = callback.data.split("_")[1]
    # Получаем текущие фильтры
    data = await state.get_data()
    filters = data.get('filters', {})
    
    # Инициализируем список курсов если нужно
    if 'majors' not in filters:
        filters['majors'] = []
    
    # Проверяем, есть ли курс уже в фильтрах
    if major in filters['majors']:
        # Удаляем курс если он уже был выбран
        filters['majors'].remove(major)
        await callback.answer(f"Курс {major} удалён", show_alert=False)
    else:
        # Добавляем курс если его ещё нет
        filters['majors'].append(major)
        await callback.answer(f"Курс {major} добавлен", show_alert=False)
    
    # Обновляем состояние
    await state.update_data(filters=filters)
    
    # Формируем текст текущих фильтров
    filter_text = "Выбранные направления: " + ", ".join(filters['majors']) if filters.get('majors') else "Фильтры не выбраны"
    
    # Редактируем сообщение, сохраняя клавиатуру
    await callback.message.edit_text(
        text=filter_text,
        reply_markup=major_select_post_kb()  # Оставляем ту же клавиатуру курсов
    )

# Кнопка назад во всех фильтрах
@router.callback_query(F.data == "back_to_filters")
async def back_to_filters_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    filters = data.get('filters', {})
    user_count_f = len(get_users_by_filters(filters))

    filter_text = "Текущие фильтры:\n"
    if filters.get('courses'):
        filter_text += f"• Курсы: {', '.join(filters['courses'])}\n"
    if filters.get('majors'):
        filter_text += f"• Направления: {', '.join(filters['majors'])}\n"
    filter_text += f"\nКоличество человек, которые будут уведомлены: {user_count_f}"
    
    await callback.message.edit_text(
        text=filter_text or "Фильтры не выбраны",
        reply_markup=filters_menu_kb()  # Возвращаем основное меню фильтров
    )

@router.callback_query(F.data == "filter_continue")
async def process_filters_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    filters = data.get('filters', {})
    event_id = data.get('event_id')
    
    if not filters:
        await callback.answer("❌ Не выбрано ни одного фильтра!", show_alert=True)
        return
    
    # Создаем клавиатуру подтверждения
    kb = await confirm_mailing_kb(event_id, filters)
    
    await callback.message.edit_text(
        f"📊 <b>Подтверждение рассылки</b>\n\n"
        f"📌 Мероприятие: {data.get('name', 'Не указано')}\n"
        f"👥 Будет оповещено: {len(get_users_by_filters(filters))} человек\n\n"
        f"Выберите действие:",
        reply_markup=kb,
        parse_mode="HTML"
    )

# В обработчике рассылки
@router.callback_query(F.data.startswith("confirm_mailing_"))
async def execute_mailing(callback: CallbackQuery, state: FSMContext, bot: Bot):
    event_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    filters = data.get('filters', {})
    event = get_event_by_id(event_id)
    
    post_text = (
        f"📢 <b>Новое мероприятие!</b>\n\n"
        f"🏷 <b>{event['name']}</b>\n"
        f"📅 <b>Когда:</b> {event['start_date']}\n"
        f"📍 <b>Где:</b> {event['location']}\n\n"
        f"{event['description']}"
    )

    users = get_users_by_filters(filters)
    
    for user in users:
        registered = is_user_registered(user['user_id'], event_id)
        try:
            if event.get('image_id'):
                await bot.send_photo(
                    chat_id=user['user_id'],
                    photo=event['image_id'],
                    caption=post_text,
                    parse_mode="HTML",
                    reply_markup=register_button(event_id, registered)
                )
            else:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=post_text,
                    parse_mode="HTML",
                    reply_markup=register_button(event_id, registered)
                )
        except Exception:
            continue

    await callback.message.edit_text(
        f"✉️ Рассылка завершена\nОхват: {len(users)} пользователей",
        parse_mode="HTML"
    )
    await state.clear()

# Обработчик регистрации
@router.callback_query(F.data.startswith("register_"))
async def process_registration(callback: CallbackQuery):
    event_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    telegram = callback.from_user.username or str(callback.from_user.id)
    
    if is_user_registered(user_id, event_id):
        await callback.answer("Вы уже зарегистрированы", show_alert=True)
        return
    
    register_user_for_event(
        user_id=user_id,
        telegram=telegram,
        event_id=event_id
    )
    
    await callback.message.edit_reply_markup(
        reply_markup=register_button(event_id, True)
    )
    
    await callback.answer(
        "✅ Вы успешно зарегистрированы!\n",
        show_alert=False
    )