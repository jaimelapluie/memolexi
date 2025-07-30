from aiogram import Bot
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand


def language_kb():
    kb_list = [
        [KeyboardButton(text="🇺🇸 английский")], [KeyboardButton(text="🇪🇸 испанский")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list,
                                   resize_keyboard=True,
                                   one_time_keyboard=True,
                                   input_field_placeholder="Выбери язык:")
    return keyboard


def check_data_kb():
    kb_list = [
        [InlineKeyboardButton(text='✅Всё окей', callback_data='correct')],
        [InlineKeyboardButton(text='❌Ой, нет, заполнить заново', callback_data='incorrect')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard


def get_login_tg_kb():
    kb_list = [
        [InlineKeyboardButton(text='Использовать мой логин из телеграм', callback_data='in_login')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard


def edit_delete_profile_kb():
    kb_list = [
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data='edit_profile')],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data='delete_profile')],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard


def edit_kb():
    kb_list = [
        [InlineKeyboardButton(text="Изменить username", callback_data="edit_username")],
        [InlineKeyboardButton(text="Изменить password", callback_data="edit_password")],
        [InlineKeyboardButton(text="Изменить имя", callback_data="edit_first_name")],
        [InlineKeyboardButton(text="Изменить email", callback_data="edit_email")],
        [InlineKeyboardButton(text="Изменить изучаемый язык", callback_data="edit_main_language")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard
    

def menu_kb():
    kb_list = [
        [KeyboardButton(text="Старт")], [KeyboardButton(text="Регистрация", callback_data="/start_questionnaire")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True, )
    return keyboard
    

async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='Начать тестовый режим'),
        BotCommand(command='start_questionnaire', description='Начать регистрацию'),
        BotCommand(command='profile', description='Посмотреть свой профиль'),
        BotCommand(command='help', description='Помощь'),
    ]
    await bot.set_my_commands(commands)
    