import asyncio
from aiogram import Bot, Dispatcher

from app.handlers import router

async def mainfunc():
    bot = Bot(token='8129239244:AAEv6S4yH6Wr2CxjzC5f4JNw-mZUliih1TQ')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:    
        asyncio.run(mainfunc())
    except KeyboardInterrupt:
        print('Бот выключен')
