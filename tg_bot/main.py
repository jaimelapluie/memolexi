from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
import os

from dotenv import load_dotenv

import asyncio
from aiogram.filters import StateFilter
from aiogram.fsm.storage.memory import MemoryStorage

from tg_bot.config import bot_instance
from tg_bot.handlers.profile.edit import edit_profile_router
from tg_bot.handlers.profile.info import info_profile_router
from tg_bot.handlers.profile.registration import questionnaire_router
from tg_bot.handlers.start import start_router
from tg_bot.keyboards.menu_kb import set_default_commands


load_dotenv()  # Загружает токен из .env файла
dp = Dispatcher(storage=MemoryStorage())

routers = [
    start_router,
    info_profile_router,
    questionnaire_router,
    edit_profile_router,
]
for router in routers:
    dp.include_router(router)


async def main():
    await set_default_commands(bot_instance)
    await dp.start_polling(bot_instance)


if __name__ == "__main__":
    asyncio.run(main())
