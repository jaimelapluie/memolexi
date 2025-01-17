from rest_framework.filters import BaseFilterBackend


class WordFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        print('def filter_queryset')
        params = request.query_params.dict()
        author = params.get('author')
        part_of_speech = params.get('part_of_speech')
        word = params.get('word')
        starts = params.get('starts')
        
        if not any([author, part_of_speech, word, starts]):
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
            
        if starts:
            queryset = queryset.filter(starts=starts)
            
        return queryset
    