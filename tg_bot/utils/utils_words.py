from aiogram.fsm.context import FSMContext

from tg_bot.config import CONST_LISTING_LIMIT, CONST_LISTING_OFFSET
from tg_bot.services.api_words import get_users_words


async def get_words_paginated(state: FSMContext, telegram_id,
                              limit=CONST_LISTING_LIMIT, offset=CONST_LISTING_OFFSET):
    # получение слов пользователя
    print("get_words_paginated")
    
    is_got, words_map = await get_users_words(telegram_id=telegram_id, limit=limit, offset=offset)
    
    if is_got and isinstance(words_map, dict):
        print(f"\nget_words_paginated  type(words_map) = {type(words_map)}")
        
        # TODO: добавить регулярные выражения для извлечения данных из ссылки  re
        # сохраняю количество записей
        next = {'limit': None, 'offset': None}
        previous = {'limit': None, 'offset': None}
        current = {'limit': limit, 'offset': offset}
        word_count = words_map.get('count')
        
        url_next = words_map.get('next')
        url_previous = words_map.get('previous')
        
        for param_dict, url in (next, url_next), (previous, url_previous):
            if url and '?limit=' in url:
                url_snippet = url.split('?limit=')[-1]
                if '&offset=' in url_snippet:
                    url_snippet = url_snippet.split('&offset=')
                    limit = url_snippet[0]
                    offset = url_snippet[1]
                    param_dict['offset'] = offset
                else:
                    limit = url_snippet
                param_dict['limit'] = limit
        
        pagination_data = {'next_word': next, 'previous_word': previous,
                           'word_count': word_count, 'to_current_words': current}
        await state.update_data(pagination_data=pagination_data)
        
        data = await state.get_data()
        print(f"data >> FMS  = {data}")
        
        words_map = words_map["results"]
        return True, words_map
    return False, None
