from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from utils.states import Mailing
from keyboards.inline import (
    filters_menu_kb,
    confirm_mailing_kb
)
from keyboards.fabrics import (
    course_select_kb,
    major_select_kb
)
from utils.database import get_event_by_id

router = Router()

@router.callback_query(F.data == 'start_mailing')
async def start_mailing_process(callback: CallbackQuery, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    event_id = data.get('event_id')
    
    if not event_id:
        await callback.answer("Ошибка: мероприятие не выбрано", show_alert=True)
        return

    # Проверяем существование мероприятия (но не показываем его)
    event = get_event_by_id(event_id)
    if not event:
        await callback.answer("Мероприятие не найдено", show_alert=True)
        return

    await callback.answer()
    
    # Сбрасываем возможные предыдущие фильтры
    await state.update_data(filters={})
    
    # Показываем меню фильтров с кнопкой "Далее"
    await callback.message.answer(
        "🔧 Выберите фильтры для рассылки:",
        reply_markup=filters_menu_kb()
    )
    
    await state.set_state(Mailing.filter_select)

# # Обработка выбора фильтров
# @router.callback_query(Mailing.filter_select, F.data.startswith("filter_"))
# async def process_filter_selection(callback: CallbackQuery, state: FSMContext):
#     filter_type = callback.data.split("_")[1]
#     await callback.answer()
    
#     data = await state.get_data()
#     filters = data.get("filters", {})
    
#     if filter_type == "course":
#         await callback.message.edit_text(
#             "🎓 Выберите курс для рассылки:",
#             reply_markup=course_select_kb()
#         )
#     elif filter_type == "major":
#         await callback.message.edit_text(
#             "📚 Выберите направление подготовки:",
#             reply_markup=major_select_kb()
#         )
#     elif filter_type == "group":
#         await callback.message.edit_text(
#             "👥 Введите номер группы (например, 101):"
#         )
#         await state.set_state(Mailing.filter_values)
#         await state.update_data(current_filter="group")
#     elif filter_type == "org":
#         await callback.message.edit_text(
#             "🏛 Выберите организацию:",
#             reply_markup=course_select_kb()
#         )
#     elif filter_type == "continue":
#         if not filters:
#             await callback.answer("❌ Не выбрано ни одного фильтра!", show_alert=True)
#             return
            
#         await callback.message.edit_text(
#             "✅ Фильтры применены. Начинаем рассылку?",
#             reply_markup=confirm_mailing_kb()
#         )
#         await state.set_state(Mailing.confirm)

# # Обработка ввода группы (текстовый ввод)
# @router.message(Mailing.filter_values, F.text)
# async def process_group_input(message: Message, state: FSMContext):
#     data = await state.get_data()
#     current_filter = data.get("current_filter")
    
#     if current_filter == "group":
#         filters = data.get("filters", {})
#         filters["group"] = message.text.strip()
        
#         await state.update_data(filters=filters)
#         await message.answer(
#             f"👥 Группа {message.text} добавлена в фильтры",
#             reply_markup=filters_menu_kb()
#         )
#         await state.set_state(Mailing.filter_select)

# # Обработка выбора значений фильтров (кнопки)
# @router.callback_query(Mailing.filter_select, F.data.startswith("select_"))
# async def process_filter_value(callback: CallbackQuery, state: FSMContext):
#     parts = callback.data.split("_")
#     filter_type = parts[1]
#     value = "_".join(parts[2:])
    
#     data = await state.get_data()
#     filters = data.get("filters", {})
    
#     if filter_type == "course":
#         filters["course"] = value
#     elif filter_type == "major":
#         filters["major"] = value
#     elif filter_type == "org":
#         filters["org"] = value
    
#     await state.update_data(filters=filters)
#     await callback.answer(f"✅ {filter_type}: {value} добавлено")
#     await callback.message.edit_text(
#         "🔧 Выберите дополнительные фильтры или продолжите:",
#         reply_markup=filters_menu_kb()
#     )

# # Подтверждение рассылки
# @router.callback_query(Mailing.confirm, F.data == "confirm_mailing")
# async def confirm_mailing(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    filters = data.get("filters", {})
    event_id = data.get("event_id")
    
    # Здесь должна быть логика рассылки по выбранным фильтрам
    # Например: get_users_by_filters(filters) и рассылка им event_id
    
    await callback.message.edit_text(
        f"✉️ Рассылка выполнена для фильтров: {filters}"
    )
    await state.clear()