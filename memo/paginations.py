from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    
class CastomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 4
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 5
    