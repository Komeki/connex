from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import sqlite3
import app.keyboards as kb

router = Router()

# Уникальные коды для проверки (временно фиксированные)
UNIQUE_CODES = {"Q"}

# Определяем состояния для FSM
class StudentRegistration(StatesGroup):
    waiting_for_code = State()
    waiting_for_fio = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Здравствуйте! Представьтесь, пожалуйста:', reply_markup=kb.student_or_curator)
    await message.delete()

@router.callback_query(F.data == 'its_a_student')
async def cmd_student(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('Отлично, студент! Для начала введите уникальный код:')

    # Устанавливаем состояние ожидания уникального кода
    await state.set_state(StudentRegistration.waiting_for_code)

    # Создаём таблицу, если её ещё нет
    with sqlite3.connect('student_bd.sql') as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,  -- id теперь будет Telegram ID пользователя
                first_name TEXT,
                middle_name TEXT,
                last_name TEXT,
                unique_code TEXT
            )
        ''')
        conn.commit()

@router.message(StateFilter(StudentRegistration.waiting_for_code))
async def process_unique_code(message: Message, state: FSMContext):
    # Проверяем уникальный код
    unique_code = message.text.strip()

    if unique_code not in UNIQUE_CODES:
        await message.answer("Ошибка: Указан неверный уникальный код. Попробуйте ещё раз.")
        return

    # Сохраняем уникальный код в состояние
    await state.update_data(unique_code=unique_code)

    # Переход к следующему шагу
    await message.answer('Код подтверждён! Теперь введите свое ФИО (например, Иванов Иван Иванович):')
    await state.set_state(StudentRegistration.waiting_for_fio)

@router.message(StateFilter(StudentRegistration.waiting_for_fio))
async def process_fio(message: Message, state: FSMContext):
    # Проверяем корректность ФИО
    fio = message.text.strip()
    parts = fio.split()

    if len(parts) != 3 or not all(part.istitle() for part in parts):
        await message.answer(
            "Ошибка: Введите ФИО корректно. Каждое слово должно начинаться с заглавной буквы. Пример: Иванов Иван Иванович"
        )
        return

    # Разделяем ФИО на части
    last_name, first_name, middle_name = parts

    # Получаем уникальный код из состояния
    data = await state.get_data()
    unique_code = data.get('unique_code')

    # Сохраняем данные в базу данных
    with sqlite3.connect('student_bd.sql') as conn:
        cur = conn.cursor()
        cur.execute(
            'INSERT OR REPLACE INTO users (id, first_name, middle_name, last_name, unique_code) VALUES (?, ?, ?, ?, ?)',
            (message.from_user.id, first_name, middle_name, last_name, unique_code)
        )
        conn.commit()

    await message.answer(f"Спасибо, {first_name}! Ваш профиль успешно заполнен.", reply_markup=kb.main_menu)

    # Сбрасываем состояние
    await state.clear()

# Обработчик кнопки "Мой профиль"
@router.message(F.text == "Мой профиль")
async def my_profile(message: Message):
    user_id = message.from_user.id

    # Подключаемся к базе данных и получаем информацию о студенте
    with sqlite3.connect('student_bd.sql') as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT first_name, middle_name, last_name, unique_code
            FROM users
            WHERE id = ?
        ''', (user_id,))
        user_data = cur.fetchone()

        # Заглушка для статистики и прав куратора
        attended_events = "\-"  # Количество посещенных мероприятий
        feedback_count = "5 \(link\)"  # Количество отзывов
        upcoming_events = "2 \(link\)"  # Предстоящие мероприятия
        conducted_events = "\-"  # Мероприятия, если пользователь куратор

    # Если пользователь найден, отображаем профиль
    if user_data:
        first_name, middle_name, last_name, unique_code = user_data
        profile_text = (
            f"*Информация о @{message.from_user.username} \(Студент\):*\n"
            f"• *ФИО:* {last_name} {first_name} {middle_name}\n"
            f"• *Направление:* ИАИТ\n"
            f"• *Курс:* 2\n"
            f"• *Группа:* 119\n"
            f"• *Номер телефона:* \+71002003040 \(может видеть только куратор\)\n"
            f"• *Организация:* Студенческий совет\n\n"
            f"*Статистика \(Студент\):*\n"
            f"• *Количество посещенных мероприятий:* {attended_events}\n"
            f"• *Отзывы о мероприятиях:* {feedback_count}\n"
            f"• *Предстоящие мероприятия:* {upcoming_events}\n\n"
            f"*Статистика \(Куратор\) \(если имеет права\):*\n"
            f"• *Количество проведенных мероприятий:* {conducted_events}"
        )
        await message.answer(profile_text, parse_mode='MarkdownV2', reply_markup=kb.back_button)
    else:
        await message.answer("Профиль не найден. Пройдите регистрацию сначала.")

@router.message(F.text == "Назад")
async def go_back(message: Message):
    # Отправляем основное меню
    await message.answer(text='Меню', reply_markup=kb.main_menu)

#################################################################################################

# Уникальные коды для проверки (временно фиксированные)
CURATOR_CODES = {"52"}

# FSM состояния для куратора
class CuratorFSM(StatesGroup):
    waiting_for_code = State()
    waiting_for_fio = State()
    waiting_for_event_info = State()
    waiting_for_event_deletion = State()

@router.callback_query(F.data == 'its_a_curator')
async def curator_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите SECRET-PHRASE:")
    await callback.message.delete()
    await state.set_state(CuratorFSM.waiting_for_code)

@router.message(StateFilter(CuratorFSM.waiting_for_code))
async def process_curator_code(message: Message, state: FSMContext):
    code = message.text.strip()  # Получаем введенный код

    if code not in CURATOR_CODES:
        await message.answer("Неверный уникальный код. Попробуйте снова.")
        return

    # Если код правильный, переходим к следующему этапу
    await message.answer("Код принят! Теперь введите ваше ФИО (например, Иванов Иван Иванович):")
    await state.set_state(CuratorFSM.waiting_for_fio)

@router.callback_query(F.data == 'its_a_curator')
async def curator_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите уникальный код куратора:")
    await callback.message.delete()
    await state.set_state(CuratorFSM.waiting_for_code)

@router.message(StateFilter(CuratorFSM.waiting_for_code))
async def process_curator_code(message: Message, state: FSMContext):
    code = message.text.strip()

    if code not in CURATOR_CODES:
        await message.answer("Неверный уникальный код. Попробуйте снова.")
        return

    await message.answer("Код принят! Теперь введите ваше ФИО (например, Иванов Иван Иванович):")
    await state.set_state(CuratorFSM.waiting_for_fio)

@router.message(StateFilter(CuratorFSM.waiting_for_fio))
async def process_curator_fio(message: Message, state: FSMContext):
    fio = message.text.strip()
    parts = fio.split()

    if len(parts) != 3 or not all(part.istitle() for part in parts):
        await message.answer(
            "Ошибка: Введите ФИО корректно. Каждое слово должно начинаться с заглавной буквы. Пример: Иванов Иван Иванович"
        )
        return

    last_name, first_name, middle_name = parts
    with sqlite3.connect('curator_bd.sql') as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS curators (
                id INTEGER PRIMARY KEY,
                fio TEXT
            )
        ''')
        cur.execute('INSERT OR REPLACE INTO curators (id, fio) VALUES (?, ?)',
                    (message.from_user.id, fio))
        conn.commit()

    await message.answer(f"Спасибо, {first_name}! Вы зарегистрированы как куратор.", reply_markup=kb.curator_panel)
    await state.clear()

# Панель куратора
@router.message(F.text == "Мой профиль")
async def curator_profile(message: Message):
    user_id = message.from_user.id
    with sqlite3.connect('curator_bd.sql') as conn:
        cur = conn.cursor()
        cur.execute('SELECT fio FROM curators WHERE id = ?', (user_id,))
        curator_data = cur.fetchone()

    if curator_data:
        fio = curator_data[0]
        await message.answer(f"Ваш профиль:\nФИО: {fio}")
    else:
        await message.answer("Профиль не найден. Вы не зарегистрированы как куратор.")

@router.message(F.text == "Добавить мероприятие")
async def add_event_start(message: Message, state: FSMContext):
    await message.answer("Введите информацию о мероприятии в формате: Название;Дата;Описание")
    await state.set_state(CuratorFSM.waiting_for_event_info)

@router.message(StateFilter(CuratorFSM.waiting_for_event_info))
async def process_event_info(message: Message, state: FSMContext):
    event_data = message.text.strip()
    try:
        title, date, description = [item.strip() for item in event_data.split(';')]
    except ValueError:
        await message.answer("Ошибка: Используйте формат 'Название;Дата;Описание'. Попробуйте снова.")
        return
    
    with sqlite3.connect('events_bd.sql') as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                date TEXT,
                description TEXT
            )
        ''')
        cur.execute('INSERT INTO events (title, date, description) VALUES (?, ?, ?)',
                    (title, date, description))
        conn.commit()

    await message.answer(f"Мероприятие добавлено:\nНазвание: {title}\nДата: {date}\nОписание: {description}", reply_markup=kb.curator_panel)
    await state.clear()

@router.message(F.text == "Удалить мероприятие")
async def delete_event_start(message: Message, state: FSMContext):
    await message.answer("Введите ID мероприятия для удаления:")
    await state.set_state(CuratorFSM.waiting_for_event_deletion)

@router.message(StateFilter(CuratorFSM.waiting_for_event_deletion))
async def process_event_deletion(message: Message, state: FSMContext):
    event_id = message.text.strip()
    if not event_id.isdigit():
        await message.answer("Ошибка: Введите корректный ID.")
        return

    with sqlite3.connect('events_bd.sql') as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM events WHERE id = ?', (int(event_id),))
        conn.commit()

    await message.answer(f"Мероприятие с ID {event_id} удалено.", reply_markup=kb.curator_panel)
    await state.clear()

@router.message(F.text == "Актуальные мероприятия")
async def view_active_events(message: Message):
    with sqlite3.connect('events_bd.sql') as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, title, date, description FROM events')
        events = cur.fetchall()

    if events:
        response = "Актуальные мероприятия:\n"
        for event in events:
            event_id, title, date, description = event
            response += f"ID: {event_id}\nНазвание: {title}\nДата: {date}\nОписание: {description}\n\n"
        await message.answer(response)
    else:
        await message.answer("Список мероприятий пуст.")

@router.message(F.text == "Статистика куратора")
async def curator_statistics(message: Message):
    with sqlite3.connect('events_bd.sql') as conn:
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM events')
        total_events = cur.fetchone()[0]

    # Заглушки для отметившихся студентов
    avg_attendees = 10  # Среднее количество отметившихся
    feedback_rate = 75  # Процент проголосовавших

    stats = (
        f"Статистика куратора:\n"
        f"• Проведено мероприятий: {total_events}\n"
        f"• Среднее количество отметившихся: {avg_attendees}\n"
        f"• Процент проголосовавших: {feedback_rate}%"
    )
    await message.answer(stats, reply_markup=kb.curator_panel)
