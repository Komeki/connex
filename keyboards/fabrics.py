from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from utils.database import get_events_paginated, get_majors_list, get_users_by_filters, get_event_by_id

# ✅ Клавиатура выбора курса для регистрации
def course_select_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for k in range(1, 7):
        builder.button(text=f"{k}", callback_data=f"course_{k}")
    builder.adjust(6)
    return builder.as_markup()

# ✅ Клавиатура выбора направления для регистрации
def major_select_kb(majors: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for major in majors:
        builder.button(text=major, callback_data=major)
    builder.adjust(2)
    return builder.as_markup()

class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int

def paginator(page: int=0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅", callback_data=Pagination(action="prev", page=page).pack()),
        InlineKeyboardButton(text="➡", callback_data=Pagination(action="next", page=page).pack()),
        width=2
    )
    return builder.as_markup()

EVENTS_PER_PAGE = 5
def event_list_kb(page: int = 0) -> InlineKeyboardMarkup:   
    events = get_events_paginated(offset=page * EVENTS_PER_PAGE, limit=EVENTS_PER_PAGE)
    builder = InlineKeyboardBuilder()

    # Кнопки мероприятий — по одной в строке, с названием и временем
    for event_id, name, time in events:
        button_text = f"{name} | {time}"
        builder.row(
            InlineKeyboardButton(text=button_text, callback_data=f"event_{event_id}"),
            width=1
        )

    # Кнопки пагинации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅", callback_data=Pagination(action="prev", page=page - 1).pack()))
    if len(events) == EVENTS_PER_PAGE:
        nav_buttons.append(InlineKeyboardButton(text="➡", callback_data=Pagination(action="next", page=page + 1).pack()))
    
    if nav_buttons:
        builder.row(*nav_buttons, width=2)

    return builder.as_markup()

def generate_events_kb(events: list, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Кнопки мероприятий
    for event in events:
        event_id, name, start_date = event
        builder.button(
            text=f"{name} | {start_date}",
            callback_data=f"event_{event_id}"
        )

    builder.adjust(1)  # по одной кнопке в строке

    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page - 1}"))
    if len(events) == EVENTS_PER_PAGE:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"page_{page + 1}"))

    if nav_buttons:
        builder.row(*nav_buttons)

    return builder.as_markup()

def course_select_post_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Кнопки 1–6
    for k in range(1, 7):
        builder.button(text=f"{k}", callback_data=f"course_{k}")
    builder.adjust(6)

    # Кнопка назад
    builder.row(
        InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_filters")
    )

    return builder.as_markup()

def major_select_post_kb(selected=None):
    if selected is None:
        selected = []
    
    # Получаем список направлений из БД
    majors = get_majors_list()
    
    # Создаем билдер
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки направлений
    for major in majors:
        builder.button(
            text=f"{'✅ ' if major in selected else ''}{major}",
            callback_data=f"major_{major}"
        )
    
    # Разбиваем на ряды по 3 кнопки
    builder.adjust(2)
    
    # Добавляем кнопки управления
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_filters")
    )
    
    return builder.as_markup()

async def confirm_mailing_kb(event_id: int, filters: dict):
    # Получаем количество пользователей для рассылки
    users_count = len(get_users_by_filters(filters))
    event = get_event_by_id(event_id)
    
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(
            text=f"✅ Подтвердить ({users_count} чел.)",
            callback_data=f"confirm_mailing_{event_id}"
        ),
        InlineKeyboardButton(
            text="✏️ Изменить фильтры",
            callback_data="edit_filters"
        )
    )
    builder.adjust(1)
    
    return builder.as_markup()

def register_button(event_id: int, is_registered: bool = False) -> InlineKeyboardMarkup:
    """
    Создает кнопку регистрации на мероприятие
    
    :param event_id: ID мероприятия
    :param is_registered: Флаг, зарегистрирован ли уже пользователь
    :return: InlineKeyboardMarkup с одной кнопкой
    """
    builder = InlineKeyboardBuilder()
    
    if is_registered:
        builder.button(
            text="✅ Вы зарегистрированы", 
            callback_data="already_registered"
        )
    else:
        builder.button(
            text="📝 Зарегистрироваться", 
            callback_data=f"register_{event_id}"
        )
    
    return builder.as_markup()