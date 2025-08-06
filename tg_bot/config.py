import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()  # загрузит из .env

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot_instance = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties())
