from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import app.keyboards as kb
 
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Здравствуйте! Представьтесь, пожалуйста:', reply_markup=kb.student_curator)

@router.message(F.text == ('Я Студент'))
async def cmd_student(message: Message):
    await message.reply('Здорово! Давай заполним твой профиль.')

@router.message(F.text == ('Я Куратор'))
async def cmd_curator(message: Message):
    await message.reply('Отлично! Вы хотите отправить запрос на получение прав куратора?', reply_markup=kb.ifcurator)

@router.callback_query(F.data == 'cur')
async def cur(callback: CallbackQuery):
    await callback.answer('Запрос отправлен')
    await callback.message.answer('Ожидайте уведомления')