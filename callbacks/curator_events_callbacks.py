from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from utils.states import CreateEvent
from utils.database import add_event, get_event_by_id, get_events_paginated

from keyboards.inline import confirm_posts, start_mailing_kb, curator_panel_events
from keyboards.curator_reply import admin_kb
from keyboards.fabrics import event_list_kb, Pagination, generate_events_kb

router = Router()

# 1 Кнопка - Создать мероприятие
# Введите название мероприятия
@router.callback_query(F.data == "curator_create_event")
async def create_event(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📝 Введите название мероприятия:")
    await state.set_state(CreateEvent.name)
# Введите описание мероприятия
@router.message(CreateEvent.name)
async def event_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("✏️ Введите описание мероприятия:")
    await state.set_state(CreateEvent.description)
# Укажите дату и время
@router.message(CreateEvent.description)
async def event_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("🕒 Укажите дату и время (например: 21 мая в 18:00):")
    await state.set_state(CreateEvent.start_time)
# Укажите место проведения
@router.message(CreateEvent.start_time)
async def event_start_time(message: Message, state: FSMContext):
    await state.update_data(start_time=message.text)
    await message.answer("📍 Укажите место проведения:")
    await state.set_state(CreateEvent.location)
# Отправьте изображение мероприятия
@router.message(CreateEvent.location)
async def event_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("📷 Отправьте изображение мероприятия:")
    await state.set_state(CreateEvent.image)
# Отправка готового поста и запроса подтверждения
@router.message(F.photo)
async def event_image(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id

    data = await state.get_data()

    add_event(
        name=data.get('name', 'Без имени'),
        description=data.get('description', ''),
        start_date=data.get('start_date', ''),
        duration=data.get('duration', ''),
        location=data.get('location', ''),
        valid=data.get('valid', ''),
        image_id=photo_id
    )

    post_text = (
        f"<b>{data.get('name', 'Без имени')}</b>\n\n"
        f"{data.get('description', '')}\n\n"
        f"🕒 <b>Время:</b> {data.get('start_time', '')}\n"
        f"📍 <b>Место:</b> {data.get('location', '')}"
    )

    await state.clear()

    # Отправляем пост с фото и текстом
    msg_post = await message.answer_photo(
        photo=photo_id,
        caption=post_text,
        parse_mode="HTML"
    )

    # Сохраняем id сообщения поста в состояние
    await state.update_data(post_msg_id=msg_post.message_id)

    # Отправляем сообщение с кнопкой "Сохранить", отвечая на пост
    await message.answer(
        'Сохранить пост?',
        reply_markup=confirm_posts(),
        reply_to_message_id=msg_post.message_id
    )
# Подтверждение и удаление сообщений - 1
@router.callback_query(F.data == "confirm_post")
async def confirmpost(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    post_msg_id = data.get('post_msg_id')

    # Удаляем сообщение с кнопкой "Сохранить пост?"
    await callback.message.delete()

    # Удаляем сообщение с постом
    await callback.message.bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=post_msg_id
    )
    
    add_event(
        name=data.get('name', 'Без имени'),
        description=data.get('description', ''),
        start_time=data.get('start_time', ''),
        location=data.get('location', ''),
        image_id=data.get('photo_id', ''),
        valid=data.get(1, ''),
    )
    
    # Отправляем новое сообщение без reply_to_message_id
    await callback.message.answer(
        "Пост сохранен ✅",
        reply_markup=admin_kb
    )
# Отмена и удаление сообщений - 2
@router.callback_query(F.data == "cancel_post")
async def confirmpost(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    post_msg_id = data.get('post_msg_id')

    # Удаляем сообщение с кнопкой "Сохранить пост?"
    await callback.message.delete()

    # Удаляем сообщение с постом
    await callback.message.bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=post_msg_id
    )
    
    # Отправляем новое сообщение без reply_to_message_id
    await callback.message.answer(
        "Пост сохранен ✅",
        reply_markup=admin_kb
    )

# ----------------------------------------------------------------------------

# 2 Кнопка - Список мероприятий
# Сам вывод списка
@router.callback_query(F.data == "curator_list_events")
async def list_events(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "📋 Список мероприятий:",
        reply_markup=event_list_kb(page=0)
    )
# Пагинация - работа кнопок перелистывания
@router.callback_query(Pagination.filter())
async def paginate(callback: CallbackQuery, callback_data: Pagination):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=event_list_kb(page=callback_data.page))
# post preview
@router.callback_query(F.data.startswith("event_"))
async def event_preview(callback: CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split("_")[1])
    event = get_event_by_id(event_id)
    await state.update_data(event_list_msg_id=callback.message.message_id)
    await state.update_data(event_id=event_id)
    if not event:
        await callback.answer("Мероприятие не найдено", show_alert=True)
        return

    post_text = (
        f"<b>{event['name']}</b>\n\n"
        f"{event['description']}\n\n"
        f"🗓 <b>Время:</b> {event['start_date']}\n"
        f"📍 <b>Место:</b> {event['location']}"
    )

    await callback.answer()

    # Отправка поста
    if event['image_id']:
        await callback.message.answer_photo(
            photo=event['image_id'],
            caption=post_text,
            reply_markup=start_mailing_kb(),
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(post_text, reply_markup=start_mailing_kb(), parse_mode="HTML")

    data = await state.get_data()
    list_msg_id = data.get("event_list_msg_id")
    if list_msg_id:
        await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=list_msg_id)
# кнопка назад
@router.callback_query(F.data == "go_back_to_events_list")
async def back_to_events(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id
        )
    await callback.message.answer(
        "📋 Список мероприятий:",
        reply_markup=event_list_kb(page=0)
    )
# ----------------------------------------------------------------------------

# 3 Кнопка - Редактирование мероприятия
@router.callback_query(F.data == "curator_edit_event")
async def edit_event(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("📦 Выполнить рассылку")

# 4 Кнопка - Редактирование мероприятия
@router.callback_query(F.data == "curator_delete_event")
async def delete_event(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("❌ Удаление мероприятия")
