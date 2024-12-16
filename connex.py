import asyncio
from aiogram import Bot, Dispatcher

from app.handlers import router
from TOKENz import token

async def mainfunc():
    bot = Bot(token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:    
        asyncio.run(mainfunc())
    except KeyboardInterrupt:
        print('Бот выключен')
