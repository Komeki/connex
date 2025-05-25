from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext


from utils.states import CreateEvent, Mailing
from utils.database import add_event, get_event_by_id, export_registrations_to_excel

from keyboards.inline import confirm_posts, start_mailing_kb
from keyboards.curator_reply import admin_kb
from keyboards.fabrics import event_list_kb, Pagination

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
    curator_id = message.from_user.id

    data = await state.get_data()
    
    # Сохраняем photo_id в состоянии для последующего использования
    await state.update_data(photo_id=photo_id, curator_id=curator_id)

    post_text = (
        f"<b>{data.get('name', 'Без имени')}</b>\n\n"
        f"{data.get('description', '')}\n\n"
        f"🕒 <b>Время:</b> {data.get('start_date', '')}\n"
        f"📍 <b>Место:</b> {data.get('location', '')}"
    )

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

# Подтверждение сохранения поста
@router.callback_query(F.data == "confirm_post")
async def confirm_post(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    data = await state.get_data()
    
    # Добавляем мероприятие в БД
    add_event(
        name=data.get('name', 'Без имени'),
        description=data.get('description', ''),
        start_date=data.get('start_date', ''),
        duration=data.get('duration', ''),
        location=data.get('location', ''),
        valid=1,
        image_id=data.get('photo_id'),
        curator_id=data.get('curator_id')
    )
    
    # Удаляем сообщение с кнопкой подтверждения
    await callback.message.delete()
    
    # Отправляем подтверждение сохранения
    await callback.message.answer(
        "Пост сохранен ✅",
        reply_markup=admin_kb
    )
    
    # Очищаем состояние
    await state.clear()

# Отмена сохранения поста
@router.callback_query(F.data == "cancel_post")
async def cancel_post(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    data = await state.get_data()
    post_msg_id = data.get('post_msg_id')
    
    # Удаляем сообщение с кнопкой подтверждения
    await callback.message.delete()
    
    # Удаляем сообщение с постом (если нужно)
    try:
        await callback.message.bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=post_msg_id
        )
    except Exception as e:
        print(f"Не удалось удалить сообщение: {e}")
    
    # Отправляем уведомление об отмене
    await callback.message.answer(
        "Создание поста отменено",
        reply_markup=admin_kb
    )
    
    # Очищаем состояние
    await state.clear()

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
        await state.set_state(Mailing.filter_select)
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
@router.callback_query(F.data == "export_registrations")
async def export_registrations_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    event_id = data.get('event_id')
    
    if not event_id:
        await callback.answer("Мероприятие не выбрано", show_alert=True)
        return
    
    try:
        # Создаем файл
        filepath = export_registrations_to_excel(event_id)
        
        # Отправляем файл пользователю
        file = FSInputFile(filepath)
        await callback.message.answer_document(
            document=file,
            caption=f"Регистрации на мероприятие"
        )
        
        # Удаляем временный файл
        filepath.unlink()
        
    except Exception as e:
        await callback.answer(f"Ошибка экспорта: {str(e)}", show_alert=True)