import asyncio

from TOKENZ import token
from aiogram import Bot, Router, Dispatcher
from handlers import reg, curator

router = Router()

async def main() -> None:
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_routers(
        reg.router,
        curator.router
    )

    await bot.delete_webhook(True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())