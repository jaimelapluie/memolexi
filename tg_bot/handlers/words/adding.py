from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from tg_bot.keyboards.words_kb import check_data_kb, get_dynamic_add_word_kb
from tg_bot.services.api_users import get_profile_by_telegram_id
from tg_bot.services.api_words import create_word
from tg_bot.states.words import AddWordProces


adding_words_router = Router()


@adding_words_router.message(Command('add_word'))
async def add_word(message: Message, state: FSMContext):
    """
    
    :param message:
    :param state:
    :return:
    """
    
    print(f"Пробую добавить слово")
    await state.clear()
    await state.set_state(AddWordProces.waiting_word)
    await message.answer(text='Введите новое слово:', reply_markup=await get_dynamic_add_word_kb(state))


@adding_words_router.message(F.text, AddWordProces.waiting_word)
async def waiting_word(message: Message, state: FSMContext):
    word: str = message.text
    word_or_expression = 'выражения' if len(word.split()) > 1 else 'слова'
    
    await state.update_data(word=word, word_or_expression=word_or_expression)
    await message.answer(text=f'Теперь введите перевод для {word_or_expression} "{word}" ',
                         reply_markup=await get_dynamic_add_word_kb(state))
    # пропустить шаг сохранить
    
    await state.set_state(AddWordProces.waiting_translation)


@adding_words_router.message(F.text, AddWordProces.waiting_translation)
async def waiting_translation(message: Message, state: FSMContext):
    translation = message.text
    data = await state.get_data()
    
    await state.update_data(translation=translation)
    await message.answer(f'Введите пример использования для "{data.get("word", 'слова, которое вы введете позже')}"',
                         reply_markup=await get_dynamic_add_word_kb(state))
    await state.set_state(AddWordProces.waiting_example)


@adding_words_router.message(F.text, AddWordProces.waiting_example)
async def waiting_example(message: Message, state: FSMContext):
    example = message.text
    data = await state.get_data()
    
    await state.update_data(example=example)
    await message.answer(f'Откуда взято это {data.get("word_or_expression")} - книга, сериал, статья?',
                         reply_markup=await get_dynamic_add_word_kb(state))
    await state.set_state(AddWordProces.waiting_source)
    

@adding_words_router.message(F.text, AddWordProces.waiting_source)
async def waiting_source(message: Message, state: FSMContext):
    source = message.text
    
    await state.update_data(source=source)
    await message.answer(f'Для удобства можно указать часть речи:',
                         reply_markup=await get_dynamic_add_word_kb(state))
    await state.set_state(AddWordProces.waiting_part_of_speech)
    

@adding_words_router.message(F.text, AddWordProces.waiting_part_of_speech)
async def waiting_part_of_speech(message: Message, state: FSMContext):
    part_of_speech = message.text
    await state.update_data(part_of_speech=part_of_speech)
    data = await state.get_data()
    
    caption = (f'Проверь, всё ли корректно? \n\n'
               f'word: {data.get("word")} \n'
               f'translation: {data.get("translation")} \n'
               f'example: {data.get("example")} \n'
               f'source: {data.get("source")} \n'
               f'part of speech: {data.get("part_of_speech")}')
    
    await message.answer(text=caption, reply_markup=check_data_kb())
    await state.set_state(AddWordProces.waiting_check_state)


@adding_words_router.callback_query(F.data == 'correct', AddWordProces.waiting_check_state)
async def waiting_submit_ok(call: CallbackQuery, state: FSMContext):
    """Подтверждение корректности введенных данных карточки слова"""
    
    await call.message.edit_reply_markup(reply_markup=None)  # удаляю кнопку
    data = await state.get_data()
    telegram_id = call.from_user.id
    username = str(await get_profile_by_telegram_id(telegram_id))
    
    print(telegram_id, username)
    
    print('!!! data', data)
    word_data = {key: data.get(key) for key in ("word", "translation", "example", "source", "part_of_speech")}
    
    is_create, service_msg = await create_word(word_data, username)
    await call.message.answer(str(word_data))
    await call.message.answer(text=f"{is_create, service_msg}")
    await state.clear()
    
 
@adding_words_router.callback_query(F.data == 'incorrect', AddWordProces.waiting_check_state)
async def waiting_submit_retry(call: CallbackQuery, state: FSMContext):
    """Отказ сохранять данные, введенные во время заполнения карточки слова. Ввод пойдет по новой"""
    
    await call.message.edit_reply_markup(reply_markup=None)  # удаляю кнопку
    await call.message.answer('Последовательность заполнения та же. Начнем с самого слова:')
    await state.set_state(AddWordProces.waiting_word)
    
    
# @adding_words_router.callback_query(F.data == 'save')
@adding_words_router.callback_query(F.data == 'skip')
async def skipping_step(call: CallbackQuery, state: FSMContext):
    
    state_tuple = (AddWordProces.waiting_word, AddWordProces.waiting_translation,
                   AddWordProces.waiting_example, AddWordProces.waiting_source,
                   AddWordProces.waiting_part_of_speech, AddWordProces.waiting_check_state,)
    
    answer_dict = {
        AddWordProces.waiting_word: 'Введите новое слово:',
        AddWordProces.waiting_translation: 'Введите перевод:',
        AddWordProces.waiting_example: 'Введите пример использования:',
        AddWordProces.waiting_source: 'Укажите источник:',
        AddWordProces.waiting_part_of_speech: 'Укажите часть речи:',
        AddWordProces.waiting_check_state: 'Проверь корректность данных:'
    }
    
    current_step = await state.get_state()
    current_step_index = state_tuple.index(current_step)
    next_step = state_tuple[current_step_index + 1]
    
    print(f'current_step = {current_step}\ncurrent_step_index={current_step_index}\nnext_step={next_step}')
    await call.message.edit_reply_markup(None)
    await call.message.answer(text=answer_dict.get(next_step))
    await state.set_state(next_step)


# await message.answer(f'Для визуализации "{data.get("word")}" можно добавить картинку')
# await state.set_state(AddWordProces.waiting_picture)


# @adding_words_router.message(F.photo, AddWordProces.waiting_picture)
# async def waiting_picture(message: Message, state: FSMContext):
#     print('Начал waiting_picture')
#     await message.answer("Ща проверим")
#     print('B')
#     data = await state.get_data()
#
#     print('C')
#     await message.answer(text=caption)