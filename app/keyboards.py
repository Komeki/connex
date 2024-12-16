from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)

# inline keyboard
student_or_curator = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Я Студент', callback_data='its_a_student'), 
                                                            InlineKeyboardButton(text='Я Куратор', callback_data='its_a_curator')]])

# reply keyboard
# keyboard = [[кнопка] ряды ] клавиатура
are_you_curator = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]], 
                                     resize_keyboard=True)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мой профиль")],
        [KeyboardButton(text="Список мероприятий")],
        [KeyboardButton(text="Мои отзывы")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

back_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

curator_panel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мой профиль")],
        [KeyboardButton(text="Добавить мероприятие"), KeyboardButton(text="Удалить мероприятие")],
        [KeyboardButton(text="Актуальные мероприятия")],
        [KeyboardButton(text="Статистика куратора")]
    ],
    resize_keyboard=True
)
