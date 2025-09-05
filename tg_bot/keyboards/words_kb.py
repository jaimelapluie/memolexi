from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from tg_bot.states.words import AddWordProces


state_dict = {
    'word': AddWordProces.waiting_word,
    'translation': AddWordProces.waiting_translation,
    'example': AddWordProces.waiting_example,
    'source': AddWordProces.waiting_source,
    'part_of_speech': AddWordProces.waiting_part_of_speech,
    'check_state': AddWordProces.waiting_check_state,
    }


def check_data_kb() -> InlineKeyboardMarkup:
    kb_list = [
        [InlineKeyboardButton(text='✅ Всё окей', callback_data='correct')],
        [InlineKeyboardButton(text='❌ Ой, нет, заполнить заново', callback_data='incorrect')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard


async def get_dynamic_add_word_kb(state: FSMContext) -> InlineKeyboardMarkup:
    print(f'Работает get_dynamic_add_word_kb')
    kb_list = []
    current_state = await state.get_state()
    state_data = await state.get_data()
    
    print(f"current_state {current_state}")
    
    has_data = any((value := state_data.get(key)) and value.strip() for key in state_dict.keys())
    if has_data:
        # print(f'has_data? {has_data}')
        kb_list.append([InlineKeyboardButton(text='✅ Сохранить', callback_data='save')])
    
    kb_list.extend([
        [InlineKeyboardButton(text='➡ Пропустить', callback_data='skip')],
        # [InlineKeyboardButton(text='❌ Отменить', callback_data='cancel')],
    ])
    keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=kb_list)
    return keyboard
