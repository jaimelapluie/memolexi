from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tg_bot.constants import LanguageChangeSource
from tg_bot.flow.common_flow import start_language_selection
from tg_bot.keyboards.words_kb import get_filter_word_kb, get_alphabet_kb, get_part_of_speech_kb
from tg_bot.prompts.word_card import FILTER_PROMPTS
from tg_bot.states.words import FilterStates

filter_words_router = Router()


@filter_words_router.callback_query(F.data == 'filter_words')
async def handle_filter_words(call: CallbackQuery, state: FSMContext):
    """
    Хэндлер предоставляющий возможность сортировки слов по дате, алфавиту (начинающиеся на букву..),
    части речи, по источнику или языку.
    Так же для увеличения лимитов для пагинации при отображении на экране.
    Ещё можно добавить количество отображаемых полей у слова или слов на странице*
    * - не обязательно
    
    Перехватывает callback data от нажатия кнопки "фильтры", отображает клавиатуру с перечнем опций.
    """
    print('\nhandle_filter_words')
    # await call.message.edit_reply_markup(reply_markup=None)  # удаляю кнопку
    await toggle_service(call, state)
    await call.message.edit_text(text='Выберите параметры для фильтрации и примените фильтр:',
                                 reply_markup=await get_filter_word_kb(state))


async def is_filter_callback(call: CallbackQuery, state: FSMContext):
    """Проверяет, что текущий callback находится в списке callback, возвращаемых по нажатию на кнопки фильтрации"""
    return call.data.startswith(('filter_date_descend', 'filter_date_ascend', 'filter_by_letter',
                                 'filter_by_part_of_speech', 'filter_by_language'))


FILTER_KEYBOARDS = {
    'filter_date_descend': get_filter_word_kb,
    'filter_date_ascend': get_filter_word_kb,
    'filter_by_letter': get_alphabet_kb,
    'filter_by_part_of_speech': get_part_of_speech_kb,
    'filter_by_language': start_language_selection
}  # TODO: подумать про билдер аля match case

filter_dict_states = {
    'filter_date_descend': None,
    'filter_date_ascend': None,
    'filter_by_letter': FilterStates.waiting_letter,
    'filter_by_part_of_speech': FilterStates.waiting_part_of_speech,
    'filter_by_language': FilterStates.waiting_language
}


async def is_filter_state(message: Message, state: FSMContext):
    """Проверяет, что текущий callback находится в списке callback, возвращаемых по нажатию на кнопки фильтрации"""
    current_state = await state.get_state()
    return current_state in {
        FilterStates.waiting_letter, FilterStates.waiting_part_of_speech, FilterStates.waiting_language}


@filter_words_router.message(is_filter_state, ~F.text.startswith('/'))
async def handle_filter_text_instead_call(message: Message, state: FSMContext):
    print('> handle_filter_text_instead_call', await state.get_data())
    await handle_filter_field(message, state)


@filter_words_router.callback_query(is_filter_callback)
async def handle_filter_field(event: CallbackQuery | Message, state: FSMContext):
    """
    Хэндлер ловит callback от кнопок в разделе фильтрации слов:
    Просмотр слов -> Фильтры ->
    'filter_date_descend', 'filter_date_ascend', 'filter_by_letter', 'filter_by_part_of_speech', 'filter_by_language'
    """
    print('\n|V|V|V|V|V Зашел в handle_filter_field (ФИЛЬТРЫ) ~~~~~~~~~~~~~~~~~~~~')
    
    if isinstance(event, Message):
        print('Текст введен там где ожидается callback. Удаляю сообщение')
        await event.delete()
        await start_language_selection(event=event, state=state)
        return
    
    else:  # isinstance(event, CallbackQuery):
        # отмечаю нажатия на кнопки фильтров и сохраняю инфо в FSM
        callback_command = event.data.split('=')[0] if '=' in event.data else event.data
        current_filter_state = filter_dict_states.get(callback_command)
        print(f'{callback_command=} {current_filter_state=}')
        await state.set_state(current_filter_state)
        await state.update_data(msg_id=event.message.message_id)  # сохраняю для редакт в start_language_selection
        press_filter_button_info = await toggle_service(call=event, state=state)
        keyboard = FILTER_KEYBOARDS.get(callback_command)
        await state.update_data(flow_source=LanguageChangeSource.FILTER_WORD,  # TODO: надо ли отключать FILTER_WORD?
                                press_filter_button_info=press_filter_button_info)
        
        if callback_command == 'filter_by_language':
            await start_language_selection(event=event, state=state)
            return
        
        prompt = FILTER_PROMPTS.get(callback_command)
        filter_keyboard = await keyboard(call=event, state=state)
        await event.message.edit_text(text=prompt, reply_markup=filter_keyboard)


# TODO: toggle service переделать в класс?
async def toggle_service(call: CallbackQuery, state: FSMContext) -> dict:
    """Сервисная функция, отмечающая нажатие на кнопки фильтров и сохраняющая инфо в FSM"""
    print('\n+++toggle_service')
    # Получаю данные о статусе нажатия на кнопки фильтров
    state_data = await state.get_data()
    press_filter_button_info: dict = state_data.get('press_filter_button_info') or dict(filter_date_descend=True)  # {}
    print(f'{state_data=}')
    
    # переключатель True/False
    if call.data in ('filter_date_descend', 'filter_date_ascend'):
        opposite = {'filter_date_descend': 'filter_date_ascend',
                    'filter_date_ascend': 'filter_date_descend'}[call.data]
        
        press_filter_button_info[call.data] = not press_filter_button_info.get(call.data, False)
        press_filter_button_info[opposite] = press_filter_button_info.get(opposite, True)
        
        # нельзя включать фильтр по уменьшению и увеличению даты одновременно
        if press_filter_button_info[call.data]:
            press_filter_button_info.pop(opposite, None)
            # press_filter_button_info[opposite] = False
        else:
            del press_filter_button_info[call.data]
    
    # кнопки второго уровня, фильтрация по конкретному параметру
    elif call.data.startswith(('filter_by_letter=', 'filter_by_part_of_speech=', 'filter_by_language=')):
        print(f"toggle_service {call.data}")
        filter_name, filter_value = str(call.data).split('=')
        current_filter_value = press_filter_button_info.setdefault(filter_name, set())
        
        # если в множестве фильтров нет нового значения, добавляем его к множеству фильтров
        if filter_value not in current_filter_value:
            current_filter_value.add(filter_value)
        
        # если нового значения есть в множестве фильтров, значит повторно нажата кнопка => фильтр отключается,
        # инфо о нажатии удаляется
        elif filter_value in current_filter_value:
            current_filter_value.remove(filter_value)
    
    # обновляю данные о нажатии на кнопки фильтров
    await state.update_data(press_filter_button_info=press_filter_button_info)
    print(press_filter_button_info)
    return press_filter_button_info
