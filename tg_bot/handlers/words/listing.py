from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tg_bot.config import CONST_LISTING_LIMIT, CONST_LISTING_OFFSET
from tg_bot.keyboards.profile_kb import language_kb
from tg_bot.keyboards.words_kb import listing_words_kb
from tg_bot.services.api_users import get_existing_token
from tg_bot.services.api_words import get_users_words
from tg_bot.utils.utils_words import get_words_paginated

viewing_words_router = Router()


def make_caption(data: list):
    print('Зашел в сборщик caption для listing', "*" * 50)
    big_caption = "Сохраненные слова:\n\n"
    for d in data:
        caption = '\n'.join(f'{d.get(key, "—")}' for key in ("word", "translation")) + "\n\n"
        big_caption += caption
    return big_caption


# get_words_paginated переехало в memolexi/tg_bot/utils/utils_words.py


@viewing_words_router.message(Command('view_words'))
async def handle_view_words(message: Message, state: FSMContext):
    """
    Показывает слова 5 штук последних и кнопку "следующие 5"
    :return:
    """
    
    print('\nЗашел в handle_view_words')
    telegram_id = message.from_user.id
    is_got, words_map = await get_words_paginated(state=state, telegram_id=telegram_id)
    
    if is_got:
        big_caption = make_caption(words_map)
        await message.answer(text=big_caption, reply_markup=await listing_words_kb(state))
    else:
        await message.answer(text='handle_view_words получить слова не удалось')


@viewing_words_router.callback_query(
    lambda new_callback: new_callback.data in ('previous_word', 'next_word', 'to_current_words'))
async def handle_view_words_next_or_prev(call: CallbackQuery, state: FSMContext):
    """
    Универсальный хэндлер для обработки нажатий на кнопки "предыдущие" или "следующие" под списком слов
    
    :param call:
    :param state:
    :return:
    """

    print(f'\nhandle_view_words_next_or_prev: нажата кнопка {call.data}~~~~ ~ ~ ~ ~ ~ ~~ ~~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~~~')
    limit, offset = CONST_LISTING_LIMIT, CONST_LISTING_OFFSET
    
    # получение пагинации из FSM
    data = await state.get_data()
    print(f"FMS >> data = {data}")
    command = call.data
    pagination_data = data.get('pagination_data')
    
    if pagination_data:
        pagination_data = pagination_data.get(command)
        limit = pagination_data.get('limit') or CONST_LISTING_LIMIT
        offset = pagination_data.get('offset') or CONST_LISTING_OFFSET
    print(f"limit, offset {limit, offset}")
    
    # получение слов пользователя
    await call.message.edit_reply_markup(reply_markup=None)
    telegram_id = call.from_user.id

    is_got, words_map = await get_words_paginated(state=state, telegram_id=telegram_id,
                                                  limit=limit, offset=offset)
    print(words_map)
    print(type(words_map))
    if is_got and isinstance(words_map, list):
        big_caption = make_caption(words_map)
        await call.message.answer(text=big_caption, reply_markup=await listing_words_kb(state))
    else:
        await call.message.answer(text='handle_view_words получить слова не удалось')
    