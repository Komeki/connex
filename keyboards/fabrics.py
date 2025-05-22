from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from utils.database import get_events_paginated

# ✅ Клавиатура выбора курса
def course_select_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for k in range(1, 7):
        builder.button(text=f"{k}", callback_data=f"course_{k}")
    builder.adjust(6)
    return builder.as_markup()

# ✅ Клавиатура выбора направления
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