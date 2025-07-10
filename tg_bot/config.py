import os
from dotenv import load_dotenv

load_dotenv()  # загрузит из .env

BOT_TOKEN = os.getenv("BOT_TOKEN")
