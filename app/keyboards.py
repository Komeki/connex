from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)

# inline keyboard
student_or_curator = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Я Студент', callback_data='its_a_student'), 
                                                            InlineKeyboardButton(text='Я Куратор', callback_data='its_a_curator')]])

# reply keyboard
# keyboard = [[кнопка] ряды ] клавиатура
are_you_curator = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]], 
                                     resize_keyboard=True)
