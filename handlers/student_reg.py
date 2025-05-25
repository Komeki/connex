from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.validate import validate_full_name

from keyboards.inline import confirm_reg
from keyboards.student_reply import student_main_kb
from keyboards.fabrics import (
    course_select_kb,
    major_select_kb,
)

from utils.states import Reg
from utils.database import (
    register_user,
    does_user_exists,
    get_majors_list,
)

router = Router()

VALID_CODES = ["SPECIAL"]

# Дополнительно: обработка нетекстовых сообщений для имени
@router.message(Reg.code, ~F.text)
async def process_invalid_name_content_type(message: Message):
    await message.answer(
        "❌ <b>Некорректный тип сообщения!</b>\n\n"
        "Пожалуйста, отправьте ваше ФИО обычным текстом.\n"
        "Фото, стикеры и другие файлы не принимаются.",
        parse_mode="HTML"
    )

# Обработка нетекстовых сообщений для группы
@router.message(Reg.group, ~F.text)
async def process_invalid_group_content_type(message: Message):
    await message.answer(
        "❌ <b>Некорректный тип сообщения!</b>\n\n"
        "Пожалуйста, отправьте данные группы обычным текстом.\n"
        "Фото, стикеры и другие файлы не принимаются.",
        parse_mode="HTML"
    )

#1 /reg - вход в состояние Reg.code для ввода специального кода
@router.message(Command(commands=["start", "reg"]))
async def start_registration(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if does_user_exists(user_id):
        await message.answer("❌ Вы уже зарегистрированы.")
        return
    
    await state.set_state(Reg.code)
    await message.answer(
        "<b>Начало регистрации.</b>\n\n"
        "Введите специальный код для доступа к регистрации:",
        parse_mode="HTML"
    )

#2 Проверка специального кода - переход к Reg.name
@router.message(Reg.code)
async def process_special_code(message: Message, state: FSMContext):
    code_text = message.text
    if code_text not in VALID_CODES:
        await message.answer('Неверный код!')
        return
    await state.set_state(Reg.name)
    await message.answer(
        "✅ <b>Код принят!</b>\n\n"
        "Теперь введите ваше ФИО:\n"
        "<i>(Пример: Иванов Иван Иванович)</i>", 
        parse_mode="HTML"
    )

#3 Сохранение Reg.name - Переход к состоянию Reg.course
@router.message(Reg.name)
async def process_name(message: Message, state: FSMContext):
    is_valid, error_message = validate_full_name(message.text)
    if not is_valid:
        await message.answer(
            f"❌ <b>Ошибка валидации:</b>\n\n"
            f"{error_message}\n\n"
            "Попробуйте еще раз:",
            parse_mode="HTML"
        )
        return

    formatted_name = " ".join(w.capitalize() for w in message.text.strip().split())
    await state.update_data(full_name=formatted_name)

    await message.answer("Выберите курс:", reply_markup=course_select_kb())
    await state.set_state(Reg.course)

# Выбор курса
@router.callback_query(Reg.course)
async def process_course(callback: CallbackQuery, state: FSMContext):
    course = int(callback.data.split("_")[1])
    await state.update_data(course=course)
    await callback.answer()

    majors = get_majors_list()
    print("MAJORS:", majors)
    await callback.message.answer(f"Всего направлений: {len(majors)}")

    await callback.message.answer("Выберите направление:", reply_markup=major_select_kb(majors))
    await state.set_state(Reg.major)

# Выбор направления
@router.callback_query(Reg.major)
async def process_major_name(callback: CallbackQuery, state: FSMContext):
    major_name = callback.data.removeprefix("major_name_")
    await state.update_data(major_name=major_name)
    await callback.answer()
    
    await callback.message.answer("Введите номер вашей группы (например, 119):")
    await state.set_state(Reg.group)

# Ввод группы
@router.message(Reg.group)
async def process_group(message: Message, state: FSMContext):
    group = message.text.strip()
    await state.update_data(group_num=group)

    data = await state.get_data()
    await message.answer(
        f"<b>Проверьте данные:</b>\n"
        f"👤 ФИО: {data['full_name']}\n"
        f"📚 Курс: {data['course']}\n"
        f"🏛 Направление: {data['major_name']}\n"
        f"👥 Группа: {data['group_num']}",
        reply_markup=confirm_reg(),
        parse_mode="HTML"
    )

# Подтверждение регистрации
@router.callback_query(F.data == "confirm_profile")
async def confirm_profile(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    register_user(
        user_id=callback.from_user.id,
        telegram=callback.from_user.username,
        full_name=data['full_name'],
        course=data['course'],
        major=data['major_name'],
        group_num=data['group_num'],
        organisation="",
        curator=0
    )

    await state.clear()
    await callback.message.edit_text("✅ Регистрация завершена!", parse_mode="HTML")
    await callback.message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=student_main_kb
    )