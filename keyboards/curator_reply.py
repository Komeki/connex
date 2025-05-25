from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Мероприятия"), KeyboardButton(text="📊 Аналитика")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)