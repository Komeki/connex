from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from utils.states import Mailing

from keyboards.inline import filters_menu_kb
from keyboards.fabrics import course_select_post_kb

from utils.database import get_event_by_id

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
    await callback.message.answer('Выберите курс: ', reply_markup=course_select_post_kb())