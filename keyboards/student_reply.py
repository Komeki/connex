from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

# Меню студента
student_main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Мероприятия"), KeyboardButton(text="📝 Мои регистрации")],
        [KeyboardButton(text="📈 Моя активность")],
        [KeyboardButton(text="👤 Профиль")],  
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню",
)