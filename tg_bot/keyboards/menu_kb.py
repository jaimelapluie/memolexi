from aiogram import Bot
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, BotCommand


def menu_kb():
    kb_list = [
        [KeyboardButton(text="Старт")], [KeyboardButton(text="Регистрация", callback_data="/start_questionnaire")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True, )
    return keyboard
    

async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='Тестовый режим'),
        BotCommand(command='start_questionnaire', description='Регистрация'),
        BotCommand(command='profile', description='Профиль'),
        BotCommand(command='help', description='Помощь'),
    ]
    await bot.set_my_commands(commands)
    