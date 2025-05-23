from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import get_majors_list, get_all_groups#, get_all_organisations

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

def start_mailing_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Перейти к рассылке", callback_data="start_mailing")],
            [InlineKeyboardButton(text="⏪ Назад", callback_data="go_back_to_events_list")]
        ]
    )

def filters_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎓 По курсу", callback_data="filter_course"), InlineKeyboardButton(text="📚 По направлению", callback_data="filter_major")],
        [InlineKeyboardButton(text="👥 По группе", callback_data="filter_group"), InlineKeyboardButton(text="🏛 По организации", callback_data="filter_org")],
        [InlineKeyboardButton(text="➡ Продолжить", callback_data="filter_continue")]
    ])

def confirm_mailing_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить рассылку", callback_data="confirm_mailing")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_mailing")]
        ]
    )