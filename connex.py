import asyncio

from TOKENz import token
from aiogram import Bot, Router, Dispatcher

from callbacks import curator_events_callbacks
from utils.database import init_db

# Регистрация
from handlers import (
    student_reg, curator_reg,
    # Захватчики сообщений
    student, curator_panel
    # Обработчики кнопок
)

router = Router()

async def main() -> None:
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_routers(
        student_reg.router,
        curator_reg.router,
        student.router,
        curator_panel.router,
        curator_events_callbacks.router
    )

    await bot.delete_webhook(True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    init_db()
    asyncio.run(main())