import django_filters
from rest_framework.filters import BaseFilterBackend

from memo.models import WordCards


class WordFilter2(django_filters.FilterSet):
    author = django_filters.NumberFilter(field_name='author')
    part_of_speech = django_filters.CharFilter(field_name='part_of_speech__part_of_speech')
    word = django_filters.CharFilter(field_name='word')
    word_starts = django_filters.CharFilter(field_name='word', lookup_expr='startswith')  # istartswith
    
    class Meta:
        model = WordCards
        fields = ['author', 'part_of_speech', 'word',]  #  ['time_create']  #


class WordFilter1(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        print('def filter_queryset')
        params = request.query_params.dict()
        author = params.get('author')
        part_of_speech = params.get('part_of_speech')
        word = params.get('word')
        word_starts = params.get('word_starts')
        
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

    
