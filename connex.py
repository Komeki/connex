import asyncio

from TOKENZ import token

from aiogram import Bot, Router, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode

from handlers import reg

router = Router()

async def main() -> None:
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_routers(
        reg.router
    )

    await bot.delete_webhook(True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())