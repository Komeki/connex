from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from keyboards.student_reply import student_main_kb

router = Router()

#1 /reg - вход в состоние Reg.code для ввода специального кода
@router.message(Command("menu"))
async def student_menu(message: Message):
    await message.answer(
        "<b>Добро пожаловать в панель студента.</b>\n"
        "Выберите действие с помощью кнопок ниже:",
        reply_markup=student_main_kb,
        parse_mode="HTML"
    )

# 📅 Мероприятия
@router.message(F.text == "📅 Мероприятия")
async def show_events(message: Message):
    await message.answer("🎉 Здесь будут отображаться предстоящие мероприятия.")

# 📝 Мои регистрации
@router.message(F.text == "📝 Мои регистрации")
async def show_my_registrations(message: Message):
    await message.answer("🗂 Здесь появятся все ваши регистрации на мероприятия.")

# 📈 Моя активность
@router.message(F.text == "📈 Моя активность")
async def show_my_activity(message: Message):
    await message.answer("📊 Здесь будет отображена ваша активность (посещения, баллы и т.д.).")

# 👤 Профиль
@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message, state: FSMContext):
    data = await state.get_data()

    name = data.get("name", "❌ Не указано")
    course = data.get("course", "❌")
    faculty = data.get("faculty", "❌")
    group = data.get("group", "❌")

    await message.answer(
        f"<b>👤 Ваш профиль</b>\n\n"
        f"<b>ФИО:</b> {name}\n"
        f"<b>Группа:</b> {course}-{faculty}-{group}\n"
        f"<b>Роль:</b> Студент 🎓",
        parse_mode="HTML"
    )
