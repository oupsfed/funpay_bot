import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import finding_lots, following_lots, information

load_dotenv()

token = os.getenv('TOKEN')
logging.basicConfig(level=logging.DEBUG)


async def main():
    bot = Bot(token=token, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_routers(following_lots.router,
                       finding_lots.router,
                       information.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
