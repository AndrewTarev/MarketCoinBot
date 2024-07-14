import asyncio
import logging

from aiogram import Bot
from aiogram import Dispatcher

from settings import BOT_TOKEN
from tg_api.commands import base_commands, get_coin_info, crud_api_keys, trading_start

dp = Dispatcher()


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp.include_routers(
        get_coin_info.router,
        base_commands.router,
        crud_api_keys.router,
        trading_start.router,
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
