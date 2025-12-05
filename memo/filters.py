import django_filters
from django.db.models import Func, IntegerField, Q
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
        print('\n WordFilter1 -> def filter_queryset')
        params = request.query_params.dict()
        
        author = params.get('author')
        word = params.get('word')
        
        parts_of_speech = params.get('parts_of_speech')
        word_starts = params.get('word_starts')
        languages = params.get('languages')
        
        print(f'{params=}')
        print(f'{author=}')
        print(f'{word=}')
        print(f'{parts_of_speech=}')
        print(f'{word_starts=}')
        print(f'{languages=}')
        
        if not any([author, parts_of_speech, word, word_starts, languages]):
            print(f'Параметров нет\n'
                  f'any([author, parts_of_speech, word, word_starts, languages])='
                  f'{any([author, parts_of_speech, word, word_starts, languages])}\n'
                  f'{[author, parts_of_speech, word, word_starts, languages]}')
            return queryset
        
        if author:
            queryset = queryset.filter(author=author)
        
        if parts_of_speech:
            q_objects = Q()
            parts = [part.strip().lower() for part in parts_of_speech.split(',') if part.strip()]
            for part in parts:
                q_objects |= Q(part_of_speech__part_of_speech=part)
            queryset = queryset.filter(q_objects)
            print(f'{q_objects=}')
            print(f'{queryset=}')
            
        if word:
            queryset = queryset.filter(word=word)
            
        # Фильтр по первой букве: word__istartswith=A,B,C
        if word_starts:
            letters = [letter.strip().upper() for letter in word_starts.split(',') if letter.strip()]
            print(letters)
            
            if letters:
                # Q объект для OR. q_objects=<Q: (OR: ('word__istartswith', 'C'), ('word__istartswith', 'P'))>
                q_objects = Q()
                for letter in letters:
                    q_objects |= Q(word__istartswith=letter)
                queryset = queryset.filter(q_objects)
                print(f'{q_objects=}')
           
        return queryset


class CustomOrderingFilter(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        print('A. CustomOrderingFilter -> filter_queryset')
        """
        Переопределяю фильтрацию, чтобы прокинуть аннотацию для длины слова
        """
        print(f'{queryset=}')
        ordering = self.get_ordering(request, queryset, view)
        print(f'{ordering=}')
        
        if ordering and any(field.lstrip('-') == 'length' for field in ordering):
            queryset = queryset.annotate(
                # length=Func('word', function='LENGTH', output_field=IntegerField())
                length=Length('word')
            )
        return super().filter_queryset(request, queryset, view)
    
    def get_ordering(self, request, queryset, view):
        print('B. CustomOrderingFilter -> get_ordering', view)
        """
        Получает порядок сортировки из параметра запроса 'ordering'.
        Если параметр отсутствует, возвращает значение по умолчанию.
        """
        # Получаем список разрешенных полей из представления
        allowed_fields = getattr(view, 'ordering_fields', None)
        print(f'{allowed_fields=}')
        ordering = super().get_ordering(request, queryset, view)
        
        # Если параметр 'ordering' не передан, используем сортировку по умолчанию
        if not ordering:
            return ['-time_create']
        
        sanitized_ordering = []
        for field in ordering:
            if field.lstrip('-') == 'length':  # это условие можно упростить elif покрывает этот случай
                sanitized_ordering.append(field)
            elif field.lstrip('-') in allowed_fields:
                sanitized_ordering.append(field)
        
        return sanitized_ordering if sanitized_ordering else None
