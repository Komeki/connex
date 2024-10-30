from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)


# reply keyboard
# keyboard = [[кнопка] ряды ] клавиатура
student_curator = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Я Студент'), KeyboardButton(text='Я Куратор')],
                                     [KeyboardButton(text='Назад')]], 
                                     resize_keyboard=True,
                                     input_field_placeholder='Выберите пункт меню...')

# inline keyboard
ifcurator = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Да', callback_data='cur'), InlineKeyboardButton(text='Нет', callback_data='nocur')]])