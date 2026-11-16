from aiogram.fsm.context import FSMContext

from tg_bot.constants import CONST_LISTING_LIMIT, CONST_LISTING_OFFSET
from tg_bot.services.api_words import get_users_words, post_srs_revision
import urllib.parse


async def build_filter_query_param(filter_info: dict) -> dict:
    """
    Функция переобразует словарь с данными об активированных фильтрах в словарь для параметров API
    :param filter_info:
    :return:
    """
    params = {}
    
    if filter_info.get("filter_date_descend"):
        params["ordering"] = "-time_create"
    elif filter_info.get("filter_date_ascend"):
        params["ordering"] = "time_create"
    
    if letters := filter_info.get("filter_by_letter"):
        if isinstance(letters, set):
            params["word_starts"] = ",".join(sorted(letters))
    
    if languages := filter_info.get("filter_by_language"):
        if isinstance(languages, set):
            params["languages"] = ",".join(sorted(languages))
    
    if parts := filter_info.get("filter_by_part_of_speech"):
        if isinstance(parts, set):
            params["parts_of_speech"] = ",".join(sorted(parts))
    
    return params
    
    
async def get_words_paginated_and_filtered(token: str, state: FSMContext,
                                           limit=CONST_LISTING_LIMIT, offset=CONST_LISTING_OFFSET):
    """
    Функция пробует получить пагинированный и фильтрованный список слов пользователя, обращаясь к API MemoLexi.
    Из полученного ответа извлекаются `next_page` и `previous` с данными о пагинации, и сохраняются
    в FSM под ключом `pagination_data` для дальнейшего использования в хэндлере `handle_view_words_next_or_prev`
    и функции `listing_words_kb`.
    
    :param token: токен для аутентификации
    :param state: для сохранения данных пагинации через FSM
    :param limit: запрашиваемое количество слов
    :param offset: запрашиваемый сдвиг
    :return: (True, words_map) - список слов в случае успеха или (False, None)
    """
    # получение слов пользователя
    print("\nget_words_paginated_and_filtered")
    
    # TODO: добавить извлечение фильтров из FSM, и учесть фильтры в зпросе
    # Извлекаю фильтры из FSM
    state_data = await state.get_data()
    filter_info = state_data.get('press_filter_button_info') or {}
    filter_param = await build_filter_query_param(filter_info)
    
    # Запрашиваю слова с фильтрами
    is_got, words_map = await get_users_words(token=token, limit=limit,
                                              offset=offset, filter_param=filter_param)
    
    if not is_got or not isinstance(words_map, dict):
        error_data = words_map
        return False, error_data
    
    print(f"\nget_words_paginated_and_filtered  type(words_map) = {type(words_map)}")
    
    # сохраняю количество записей и пагинацию
    word_count = words_map.get('count')
    current_page = {'limit': limit, 'offset': offset}
    
    # Извлекаю ТОЛЬКО limit/offset из next/previous
    next_page = extractor_limit_offset(words_map.get('next'))
    previous_page = extractor_limit_offset(words_map.get('previous'))
    
    print(next_page)
    print(previous_page)
    print(current_page)
    print('<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>')
    
    pagination_data = {
        'next_word': next_page,
        'previous_word': previous_page,
        'word_count': word_count,
        'to_current_words': current_page,
    }
    
    await state.update_data(pagination_data=pagination_data)
    print(f"data >> FMS  = {await state.get_data()}")
    words_map = words_map["results"]
    return True, words_map


def extractor_limit_offset(url: str | None) -> dict:
    """Извлекает ТОЛЬКО limit и offset из URL. Всё остальное игнорирует"""
    if not url:
        return {"limit": None, "offset": None}
    
    parsed = urllib.parse.urlparse(url, allow_fragments=True)
    query_params = urllib.parse.parse_qs(parsed.query)
    
    limit = query_params.get('limit', [None])[0]
    offset = query_params.get('offset', [None])[0]
    
    return {'limit': limit, 'offset': offset}


# TODO: вынести SRS сессии в сервис
class SRSService:
    # def __init__(self, words: list) -> dict:
    #     self.words = words
    #     ...
    
    @staticmethod
    async def commit_revision(revision_list, token):
        """
        Вызывается из handle_srs_process, получает список из словарей {id слова: quality (оценка сложности)}, и
        обращается к сервисной функции работающей с API post_srs_revision.
        
        Возвращает (True, response) - в случае успеха, а иначе - (False, response).
        """
        print('\nSRSService.commit_revision')
        is_got, response = await post_srs_revision(revision_list, token)
        
        if is_got:
            return True, response
        return False, response
    