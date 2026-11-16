from aiogram.exceptions import TelegramBadRequest
from functools import wraps
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from tg_bot.constants import LanguageChangeSource
from tg_bot.keyboards.profile_kb import get_language_profile_kb
from tg_bot.keyboards.words_kb import get_language_word_kb
from tg_bot.prompts.common import EDIT_WORD_FIELD_PROMPT
from tg_bot.prompts.language import language_selection_prompt, edit_word_language_prompt
from tg_bot.prompts.word_card import build_word_card_caption
from tg_bot.services.api_references import get_languages_list


def ignore_not_modified(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                print('Просто игнорируем - сообщение такое же')
                return None
            else:
                raise  # Все остальные BadRequest пробрасываем дальше
    
    return wrapper


@ignore_not_modified
async def edit_message_safe(bot, **kwargs):
    """Безопасное редактирование сообщения - если будет ошибка телеги (сообщение такое же), декоратор
    все отработает и проглотит ошибку"""
    return await bot.edit_message_text(**kwargs)


def get_msg_id(event, state_data):
    print('> get_msg_id -- получение id сообщения для редактирования')
    msg_id = state_data.get('msg_id')
    print(msg_id)
    if msg_id is None:
        raise ValueError("msg_id отсутствует в state")
    
    if (isinstance(event, Message) and
            state_data.get('flow_source') in {LanguageChangeSource.SRS, LanguageChangeSource.ADD_WORD}):
        msg_id += 1
    return msg_id


async def build_language_selection_content(event: Message | CallbackQuery, state_data: dict,
                                           languages_list: list[dict] | None = None
                                           ) -> tuple[str, InlineKeyboardMarkup]:
    """Возвращает (text, reply_markup) в зависимости от источника"""
    print('>> build_language_selection_content')
    flow_source = state_data.get('flow_source')
    word_card = state_data.get('word_card')
    field = state_data.get('field')

    match flow_source:
        case LanguageChangeSource.ADD_WORD:
            print('++++++ ADD_WORD редактирую')
            if isinstance(event, Message):
                text = language_selection_prompt(flow_source).warning
            else:
                text = language_selection_prompt(flow_source).main
            reply_markup = await get_language_word_kb(languages_list=languages_list, flow_source=flow_source)

        case LanguageChangeSource.EDIT_WORD:
            print('++++++ EDIT_WORD редактирую')
            word_id = state_data.get('word_id', None)
            word = state_data.get('word', None)
            if isinstance(event, Message):
                print('EDIT_WORD Message')
                text = EDIT_WORD_FIELD_PROMPT.format(
                    field=field, word_card=build_word_card_caption(word_card),
                    field_prompt=language_selection_prompt(flow_source).warning)
            else:
                text = edit_word_language_prompt(word_card)
            reply_markup = await get_language_word_kb(languages_list=languages_list, word_id=word_id, word=word,
                                                      flow_source=flow_source)

        case LanguageChangeSource.SRS:
            print('++++++ SRS редактирую')
            if isinstance(event, Message):
                text = language_selection_prompt(flow_source).warning
            else:
                text = language_selection_prompt(flow_source).main
            reply_markup = await get_language_word_kb(languages_list=languages_list, flow_source=flow_source)

        case LanguageChangeSource.PROFILE:
            print('++++++ PROFILE редактирую')
            if isinstance(event, Message):
                text = language_selection_prompt(flow_source).warning
            else:
                text = language_selection_prompt(flow_source).main
            reply_markup = await get_language_profile_kb(languages_list=languages_list, flow_source=flow_source)

        case LanguageChangeSource.FILTER_WORD:
            print('++++++ FILTER_WORD редактирую')
            press_filter_button_info = state_data.get('press_filter_button_info') or {}
            if isinstance(event, Message):
                current_filters = press_filter_button_info.get('filter_by_language', set())
                text = language_selection_prompt(flow_source).warning
                reply_markup = await get_language_word_kb(languages_list=languages_list,
                                                          current_filters=current_filters, flow_source=flow_source)
            else:
                filter_name, _ = (str(event.data).split('=', 1) + [None])[:2]
                current_filters = press_filter_button_info.get(filter_name, set())
                
                print(f'{press_filter_button_info=}')
                print(f'{current_filters=} {type(current_filters)}')
                text = language_selection_prompt(flow_source).main

                reply_markup = await get_language_word_kb(
                    languages_list=languages_list, current_filters=current_filters,
                    flow_source=flow_source)
        case _:
            raise ValueError(f"Неизвестный flow_source: {flow_source}")
    print('завершение build_language_selection_content')
    return text, reply_markup


async def start_language_selection(event: Message | CallbackQuery, state: FSMContext):
    """Функция, редактирующая текущие сообщения, присылая сообщение с клавиатурой с языками."""
    print(f'\nVVVVVVVVVVV flow -> common_flow -> start_language_selection VVVVVVVVV statedata={await state.get_data()}')
    
    state_data = await state.get_data()
    is_got, languages_list = await get_languages_list()
    if not is_got:
        languages_list = None
    text, reply_markup = await build_language_selection_content(event=event, state_data=state_data,
                                                                languages_list=languages_list)
    print(f'приступаю к редактированию сообщения начало-->{text}<--конец сообщения')
    if isinstance(event, Message):
        bot = event.bot
        await edit_message_safe(bot, chat_id=event.chat.id, message_id=get_msg_id(event, state_data),
                                text=text, reply_markup=reply_markup)
    else:
        await event.message.edit_text(text=text, reply_markup=reply_markup)
