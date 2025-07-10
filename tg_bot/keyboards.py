from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


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
        [InlineKeyboardButton(text='Использовать мой логин из телеграма', callback_data='in_login')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard
