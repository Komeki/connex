from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import sqlite3
import app.keyboards as kb
 
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Здравствуйте! Представьтесь, пожалуйста:', reply_markup=kb.student_or_curator)
    await message.delete()

@router.callback_query(F.data == ('its_a_student'))
async def cmd_student(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Отлично, студент, давайте заполним Ваш профиль!')
    await callback.message.answer('Введите свое ФИО: ')

    conn = sqlite3.connect('student_bd.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50))')
    conn.commit()
    cur.close()
    conn.close()

@router.callback_query(F.data == 'its_a_curator')
async def z(callback: CallbackQuery):
    await callback.message.answer('Введите SECRET-PHRASE: ')
    await callback.message.delete
