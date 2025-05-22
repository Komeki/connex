from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from utils.roles import admin_required
from keyboards.curator_reply import admin_kb
from keyboards.inline import confirm_reg_admin
from utils.states import AdminReg
from utils.database import save_admin
from utils.validate import validate_full_name

router = Router()

# /make_admin
@router.message(Command("make_admin"))
async def cmd_make_admin(message: Message, command: CommandObject, state: FSMContext):
    args = command.args
    if args != '119':
        await message.answer("⛔ Неверный код доступа.")
        return

    await message.answer("Введите ваше ФИО:")
    await state.set_state(AdminReg.waiting_for_fullname)

@router.message(AdminReg.waiting_for_fullname)
async def process_fullname(message: Message, state: FSMContext):
    full_name=message.text
    is_valid, error_message = validate_full_name(full_name)

    if not is_valid:
        await message.answer(
            f"❌ <b>Ошибка валидации:</b>\n\n"
            f"{error_message}\n\n"
            "Попробуйте еще раз:",
            parse_mode="HTML"
        )
        return
    
    formatted_name = " ".join(word.capitalize() for word in full_name.strip().split())
    await state.update_data(full_name=formatted_name)

    await message.answer("Введите ваш статус (например: Председатель Студенческого совета):")
    await state.set_state(AdminReg.waiting_for_status)

@router.message(AdminReg.waiting_for_status)
async def process_status(message: Message, state: FSMContext):
    status_text = message.text
    await state.update_data(status_text=status_text)
    
    data = await state.get_data()
    await message.answer(
        f"<b>Введенные данные:</b>\n"
        f"ФИО: {data['full_name']}\n"
        f"Статус: {data['status_text']}\n",
        reply_markup=confirm_reg_admin(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "confirm_profile_admin")
async def confirm_profile(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    user_id = callback.from_user.id
    full_name = data.get("full_name")
    status_text = data.get("status_text")
    
    save_admin(user_id=user_id, full_name=full_name, status_text=status_text)
    
    await state.clear()
    await callback.message.edit_text("✅ <b>Регистрация администратора завершена!</b>", parse_mode="HTML")
    await callback.message.answer(
        "<b>Добро пожаловать в админ-панель.</b>\n"
        "Выберите действие с помощью кнопок ниже:",
        reply_markup=admin_kb,
        parse_mode="HTML"
    )

# Команда /admin - reply-клавиатура
@router.message(Command("admin"))
@admin_required
async def admin_panel(message: Message):
    await message.answer(
        "<b>Добро пожаловать в админ-панель.</b>\n"
        "Выберите действие с помощью кнопок ниже:",
        reply_markup=admin_kb,
        parse_mode="HTML"
    )
