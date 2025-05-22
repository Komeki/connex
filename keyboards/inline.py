from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def confirm_reg():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_profile")
        ]
    ]
)

def confirm_reg_admin():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_profile_admin")
        ]
    ]
)

def confirm_posts():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Сохранить", callback_data="confirm_post"),
            InlineKeyboardButton(text="❌ Не сохранять", callback_data="cancel_post")
        ]
    ]
)

def curator_panel_events():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Создать мероприятие", callback_data="curator_create_event")],
        [InlineKeyboardButton(text="📋 Список моих мероприятий", callback_data="curator_list_events")],
        [InlineKeyboardButton(text="📦 Выполнить рассылку", callback_data="curator_edit_event")],
        [InlineKeyboardButton(text="❌ Удалить мероприятие", callback_data="curator_delete_event")],
    ])