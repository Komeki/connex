from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.validate import validate_full_name

from keyboards import inline
from keyboards.student_reply import student_main_kb

import re

from utils.states import Reg
from utils.database import register_user
from utils.database import does_user_exists

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
@router.message(Command("reg"))
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
    if code_text in VALID_CODES:
        await state.set_state(Reg.name)
        await message.answer(
            "✅ <b>Код принят!</b>\n\n"
            "Теперь введите ваше ФИО:\n"
            "<i>(Пример: Иванов Иван Иванович)</i>", 
            parse_mode="HTML"
        )
    else:
        await message.answer('Неверный код!')
        return

#3 Сохранение Reg.name - Переход к состоянию Reg.group
@router.message(Reg.name)
async def process_name_with_function(message: Message, state: FSMContext):
    name_text = message.text
    is_valid, error_message = validate_full_name(name_text)

    if not is_valid:
        await message.answer(
            f"❌ <b>Ошибка валидации:</b>\n\n"
            f"{error_message}\n\n"
            "Попробуйте еще раз:",
            parse_mode="HTML"
        )
        return

    formatted_name = " ".join(word.capitalize() for word in name_text.strip().split())
    await state.update_data(full_name=formatted_name)
    await state.set_state(Reg.group)

    await message.answer(
        "Введите данные в формате:\n\n<code>2-ИАИТ-119</code>\n\n"
        "<i>(Курс-Факультет-Группа)</i>",
        parse_mode="HTML"
    )

#4 Сохранение состояния Reg.group - Кнопка подтверждения данных 
@router.message(Reg.group)
async def process_group(message: Message, state: FSMContext):
    match = re.match(r"^(\d+)-([а-яА-Яa-zA-Z]+)-(\d+)$", message.text.strip())
    if not match:
        await message.answer("❌ Неверный формат. Попробуйте снова: <code>2-ИАИТ-119</code>", parse_mode="HTML")
        return

    course, faculty, group_num = match.groups()
    await state.update_data(course=course, faculty=faculty, group_num=group_num)

    data = await state.get_data()

    await message.answer(
        f"<b>Введенные данные:</b>\n"
        f"ФИО: {data['full_name']}\n"
        f"Группа: {course}-{faculty}-{group_num}",
        reply_markup=inline.confirm_reg(),
        parse_mode="HTML"
    )

#5 Подтверждение данных - Выход из регистрации
@router.callback_query(F.data == "confirm_profile")
async def confirm_profile(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    telegram = callback.from_user.username

    register_user(
        user_id=user_id,
        telegram=telegram,
        full_name=data['full_name'],
        course=data['course'],
        faculty=data['faculty'],
        group_num=data['group_num'],
        organisation=data.get('organisation', ""),
        curator=0
    )

    await state.clear()
    await callback.message.edit_text("✅ <b>Регистрация завершена!</b>", parse_mode="HTML")
    await callback.message.answer(
        "<b>Добро пожаловать в панель студента.</b>\n"
        "Выберите действие с помощью кнопок ниже:",
        reply_markup=student_main_kb,
        parse_mode="HTML"
    )