from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from utils.database import get_events_paginated

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