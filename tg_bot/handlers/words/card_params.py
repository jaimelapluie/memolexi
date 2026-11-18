from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from tg_bot.constants import LanguageChangeSource
from tg_bot.flow.common_flow import start_language_selection
from tg_bot.flow.profile_flow import update_user_data_and_sync_state
from tg_bot.flow.words_flow import update_word_and_sync_state
from tg_bot.handlers.words.new_adding import handle_start_add_word
from tg_bot.keyboards.profile_kb import get_edit_profile_kb
from tg_bot.keyboards.words_kb import edit_word_kb
from tg_bot.prompts.common import SUCCESS_UPDATED, EDIT_WORD_NEXT_ACTION, EDIT_PROFILE_MODE_PROMPT
from tg_bot.prompts.profile_card import build_profile_card_caption

from tg_bot.prompts.word_card import build_word_card_caption
from tg_bot.services.srs_service import begin_srs_session


card_params_router = Router()


@card_params_router.callback_query(F.data == 'change_language')
async def handle_change_language(call: CallbackQuery, state: FSMContext, token: str):
    """
    Хэндлер отрабатывает callback полученный из get_dynamic_add_word_kb, вызванной в handle_start_add_word.
    Хэндлер редактирует сообщение с просьбой ввести слово, и вместо текущего языка просит выбрать новый язык,
    а так же показывает клавиатуру с перечнем языков.
    """
    
    print('\n⚪VVVVVV handle_change_language  VVVVV')
    current_state = await state.get_state()
    state_data = await state.get_data()
    
    print(f'{current_state=}')
    if current_state == 'AddWordProcess:waiting_word':
        flow_source = LanguageChangeSource.ADD_WORD
    elif state_data.get('flow_source') == LanguageChangeSource.SRS:  # TODO: нет состояния для SRS, надо ли?
        flow_source = LanguageChangeSource.SRS
    else:
        print('Ошибка, неизвестный сценарий')
        flow_source = None
    await state.update_data(flow_source=flow_source)
    await start_language_selection(call, state)


# TODO: продумать поэлегантнее возврат к изначальному хэндлеру
# TODO: перенести в нейтральный слой - т.к. тут сценарии и words и profile
@card_params_router.callback_query(lambda new_callback: str(new_callback.data).startswith('language_code='))
async def handle_save_language(call: CallbackQuery, state: FSMContext, token):
    """
    Хэндлер используется во время сценария добавления нового слова, а именно при смене языка.
    Хэндлер перехватывает callback от нажатия на кнопку клавиатуры get_language_word_kb и get_language_profile_kb
    после выбора языка (см. предыдущий шаг).
    Применяет изменения и вносит их в БД в таблицу User поле main_language.
    Хэндлер редактирует сообщение с просьбой ввести слово, и вместо просьбы выбрать новый язык отображает выбранный,
    а так же показывает клавиатуру get_dynamic_add_word_kb.
    """
    
    print(f'\n⚪VVVVVVVVV  Зашел в handle_save_language VVVVVVVVV {call.data=}')
    
    field_name = 'language_code'
    language_code = call.data.split('&')[0].split('=')[1]
    language = call.data.split('&')[1].split('=')[1]
    
    print(f'...language_code + language --> {language_code}{language}')
    
    current_state = await state.get_state()
    state_data = await state.get_data()
    flow_source: LanguageChangeSource = state_data.get('flow_source')
    print(f'.. {current_state=}')
    
    # редактирование языка слова
    if flow_source == LanguageChangeSource.EDIT_WORD:
        word_id = state_data.get('word_id')
        word_data = {"word_id": word_id, field_name: language_code}
        print(f'{word_data=}')
        
        is_updated, service_msg, word_card = \
            await update_word_and_sync_state(word_data=word_data, state=state, token=token)
        
        if is_updated:
            await call.message.edit_text(
                text=f'{SUCCESS_UPDATED}\n\n'
                     f'{build_word_card_caption(word_card)}\n\n'
                     f'{EDIT_WORD_NEXT_ACTION}',
                reply_markup=await edit_word_kb())
        else:
            await call.message.edit_text(service_msg)
        await state.set_state(None)  # иначе висит EditWord.waiting_edit_language
        await pop_flow_source(state)
        return
    
    # редактирование языка пользователя (в сценариях ADD_WORD, SRS и PROFILE)
    user_data = {"telegram_id": call.from_user.id, field_name: language_code}
    print(f"данные для обновления: {user_data}\n")
    
    # меняю язык в БД
    is_updated, profile_data_or_error = await update_user_data_and_sync_state(user_data, field_name, state)
    
    # TODO: ОПЯТЬ
    print(f'до апдейт {await state.get_data()=}')
    await state.update_data(language_code=language_code, language=language)
    print(f'после апдейт {await state.get_data()=}')
    
    if is_updated and flow_source == LanguageChangeSource.ADD_WORD:
        print('Перенаправляю в handle_start_add_word')
        print(f'еще разок посмотрим что там в {await state.get_data()=}')
        await pop_flow_source(state)
        await handle_start_add_word(call, state)
        
    elif is_updated and flow_source == LanguageChangeSource.SRS:
        print('Перенаправляю в begin_srs_session')
        await pop_flow_source(state)
        await begin_srs_session(call, state, token)
    
    elif is_updated and flow_source == LanguageChangeSource.PROFILE:
        print('handle_save_language (PROFILE) -> пишу сообщение прям тут')
        await pop_flow_source(state)
        profile_data = profile_data_or_error
        # TODO: в process_field_input есть похожий блок
        await call.message.edit_text(
            text=f'{SUCCESS_UPDATED}\n\n'
                 f'{EDIT_PROFILE_MODE_PROMPT.format(profile_card=build_profile_card_caption(profile_data))}',
            reply_markup=await get_edit_profile_kb())
    
    else:
        await call.message.edit_text(text='Ошибка! Язык не сохранен. \n(handle_save_language)')
        raise ValueError(profile_data_or_error)


async def pop_flow_source(state: FSMContext):
    """Вынес обнуление flow_source для переиспользования"""
    state_data = await state.get_data()
    state_data.pop('flow_source')
    await state.set_data(state_data)
    