import django_filters
from django.db.models import Func, IntegerField
from django.db.models.functions import Length
from rest_framework.filters import BaseFilterBackend, OrderingFilter

from memo.models import WordCards


class WordFilter2(django_filters.FilterSet):
    author = django_filters.NumberFilter(field_name='author')
    part_of_speech = django_filters.CharFilter(field_name='part_of_speech__part_of_speech')
    word = django_filters.CharFilter(field_name='word')
    word_starts = django_filters.CharFilter(field_name='word', lookup_expr='startswith')  # istartswith
    
    class Meta:
        model = WordCards
        fields = ['author', 'part_of_speech', 'word', ]  # ['time_create']  #


class WordFilter1(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        print('def filter_queryset')
        params = request.query_params.dict()
        author = params.get('author')
        part_of_speech = params.get('part_of_speech')
        word = params.get('word')
        word_starts = params.get('starts')
        
        if not any([author, part_of_speech, word, word_starts]):
            return queryset
        
        if author:
            queryset = queryset.filter(author=author)
        
        if part_of_speech:
            if part_of_speech.isdigit():
                queryset = queryset.filter(part_of_speech=part_of_speech)
            else:
                queryset = queryset.filter(part_of_speech__part_of_speech=part_of_speech)
        
        if word:
            queryset = queryset.filter(word=word)
        
        if word_starts:
            queryset = queryset.filter(word__startswith=word_starts)
        
        return queryset


class CustomOrderingFilter(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        print('A filter_queryset')
        """
        Переопределяю фильтрацию, чтобы прокинуть аннотацию для длины слова
        """
        ordering = self.get_ordering(request, queryset, view)
        
        if ordering and any(field.lstrip('-') == 'length' for field in ordering):
            queryset = queryset.annotate(
                # length=Func('word', function='LENGTH', output_field=IntegerField())
                length=Length('word')
            )
        return super().filter_queryset(request, queryset, view)
    
    def get_ordering(self, request, queryset, view):
        print('B get_ordering', view)
        """
        Получает порядок сортировки из параметра запроса 'ordering'.
        Если параметр отсутствует, возвращает значение по умолчанию.
        """
        # Получаем список разрешенных полей из представления
        allowed_fields = getattr(view, 'ordering_fields', None)
        ordering = super().get_ordering(request, queryset, view)
        
        # Если параметр 'ordering' не передан, используем сортировку по умолчанию
        if not ordering:
            return ['-time_create']  # Замените на поле по умолчанию для вашей модели
        
        sanitized_ordering = []
        for field in ordering:
            if field.lstrip('-') == 'length':
                sanitized_ordering.append(field)
            elif field.lstrip('-') in allowed_fields:
                sanitized_ordering.append(field)
        
        return sanitized_ordering if sanitized_ordering else None
