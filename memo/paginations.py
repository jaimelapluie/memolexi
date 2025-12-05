from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    
class CastomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 5
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 50
    
"""
new file:   common/__init__.py  папка добавлена
renamed:    memo/constants.py -> common/constants.py  файл перенес в common
new file:   common/validators.py добавлен файл для валидаторов общих
modified:   memo/admin.py  откорректированы импорты
modified:   memo/models.py  откорректированы импорты и FK
modified:   memo/serializers.py  откорректированы импорты
new file:   references/__init__.py  добавлено приложение для выноса справочных таблиц
new file:   references/admin.py
new file:   references/apps.py
new file:   references/fixtures/initial_references.json данные справочных таблиц для загрузки
new file:   references/fixtures/review_history.json  данные для восстановления
new file:   references/models.py  перенесены модели PartOfSpeech и Language
new file:   references/tests.py
new file:   references/views.py
modified:   users/models.py  откорректированы  FK


new file:   common/__init__.py
        renamed:    memo/constants.py -> common/constants.py
        new file:   common/validators.py
        modified:   memo/admin.py
        modified:   memo/models.py
        modified:   memo/serializers.py
        modified:   memolexi/settings.py
        new file:   references/__init__.py
        new file:   references/admin.py
        new file:   references/apps.py
        new file:   references/fixtures/exported_wordcards.json
        new file:   references/fixtures/initial_references.json
        new file:   references/fixtures/review_history.json
        references/fixtures/wordcards_links_only.json
        references/fixtures/wordcards_only.json
        references/fixtures/wordlists_only.json
        references/models.py
        references/tests.py
        references/views.py
        users/models.py
"""