from typing import Any

from django.contrib.auth.models import Group, User
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, serializers
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

from memo.filters import WordFilter1, WordFilter2, CustomOrderingFilter
from memo.models import WordCards, PartOfSpeech, WordCardsList  # Snippet
from memo.paginations import CustomPageNumberPagination, CastomLimitOffsetPagination
from memo.permissions import IsOwnerOrReadOnly
from memo.serializers import WordSerializer, UserSerializer  # SnippetSerializer, GroupSerializer
from django.http import JsonResponse, Http404

from rest_framework.decorators import api_view

from rest_framework.reverse import reverse
from rest_framework import renderers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from memo.services import WordService
from memo.tasks.word_transfer import WordTransfer


# def wording(request):
#     queryset = WordCards.objects.all()
#     serializer = WordSerializer(queryset, many=True)
#     return JsonResponse(serializer.data, safe=False)


class WordDetail(APIView):
    def get_object(self, pk):
        try:
            return WordCards.objects.get(id=pk)
        except WordCards.DoesNotExist:
            raise Http404('Запись не найдена (get_object)')
    
    def get(self, request, pk):
        
        print(request.query_params)
        word = self.get_object(pk)  # Получаем объект записи
        serializer = WordSerializer(word)
        return Response(serializer.data)  # Возвращаем данные
    
    def put(self, request, pk, format=None):
        word = self.get_object(pk)
        serializer = WordSerializer(word, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        word = self.get_object(pk)
        word.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Wording(APIView):
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = WordFilter2
    
    # filter_backends = [WordFilter1, CustomOrderingFilter]
    filter_backends = [CustomOrderingFilter]
    ordering_fields = ['word', 'translation', 'time_create', 'length']
    
    pagination_class = CastomLimitOffsetPagination  # CustomPageNumberPagination
    
    def get(self, request):
        # queryset = (WordCards.objects
        #             .select_related('part_of_speech')
        #             .prefetch_related('wordcards_links__word_lists')
        #             .all())
        
        queryset = (
            WordCards.objects
            .select_related('part_of_speech')
            .prefetch_related(
                Prefetch(
                    'wordcards_links',
                    queryset=WordCardsList.objects.select_related('word_lists').only('word_lists__name',
                                                                                     'word_lists__author')
                )
            )
            .all()
        )
        
        # Применяем фильтры
        for beckend_instance in self.filter_backends:
            queryset = beckend_instance().filter_queryset(request=request, queryset=queryset, view=self)
        
        # Применяем пагинацию
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        serializer = WordSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)  # Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        print(request.data)
        serializer = WordSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            try:
                # Если записи нет, создаём новую
                word, created = WordService.create_word_with_master_list(serializer.validated_data, request.user)
            except Exception as e:
                return Response({"error_from Wording.post": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            if created:
                print('wording/post зашел')
                return Response(WordSerializer(word).data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'message': f'{serializer.validated_data.get("word")} is already exists'},
                    status=status.HTTP_409_CONFLICT
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    def get(self, request):
        usernames = User.objects.all()
        serializer = UserSerializer(usernames, many=True)
        print('A', type(usernames), usernames)
        print('B----')
        print(serializer)
        print('C----')
        print(serializer.data[0])
        return JsonResponse(serializer.data, safe=False)
        # return Response(*usernames, status=status.HTTP_200_OK)


class UploadWordsView(APIView):
    def get(self, request):
        return Response({
            "info": "Send me a link to the file with the words or empty request (for using default file)",
            "Expected format": " 'link': '<folder link>' "},
                        status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        link = request.data.get('link')  # ссылка из запроса
        message = "Words from the main link were used"
        if link:  # если ссылка дана, то сообщение уже другое - со ссылкой
            message = f"Words from the new link: {link}"
        
        # Обрабатываю файл через WordTransfer
        word_transfer = WordTransfer(link_source=link)  # экземпляр парсера заряженный ссылкой
        words = word_transfer.parser()  # парсер возвращает список слов

        created_words = []
        existing_words = []
    
        for word in words:
            serializer = WordSerializer(data=word)
            print('UploadWordsView', word)
            if serializer.is_valid():
                try:
                    # Если записи нет, создаём новую
                    print('!!2')
                    print('loop1', serializer)
                    # print('loop2', serializer.data)
                    print('loop2', word, type(word))
                    print('!!3')
                    instance, created = WordService.create_word_with_master_list(word, request.user)
                    print('>', instance, created)
                except Exception as e:
                    return Response({"error_from Wording.post": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
                if created:
                    print(type(instance))
                    created_words.append(instance.word)
                else:
                    existing_words.append(instance.word)

        return Response({
            "message": message,
            "created_words": [str(word) for word in created_words],
            "existing_words": [str(word) for word in existing_words],
        }, status=status.HTTP_201_CREATED)
    
    # def post(self, request, *args, **kwargs):
    #     link = request.data.get('link')
    #     print(request.data.get('link'))
    #     message = "Words from the main link were used"
    #     if link:
    #         from pathlib import Path
    #         normalized_path = Path(link)
    #         print(normalized_path)
    #         message = f"Words from the new link: {normalized_path}"
    #
    #     # Обрабатываю файл через WordTransfer
    #     word_transfer = WordTransfer(link_source=link)
    #     words = word_transfer.parser()
    #     res = WordSerializer(data=words, many=True)
    #     print(res.is_valid())
    #     print(res.validated_data)
    #     # res.save()
    #
    #     return Response({"message": message}, status=200)



# {"link": "D:\Obsidian_notes\jaime\English\Vocab_Memolexi — копия.md"}
# {"link": "D:\\Obsidian_notes\\jaime\\English\\Vocab_Memolexi — копия.md"}

# class UserView(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#


#####################################
# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     This viewset automatically provides `list` and `retrieve` actions.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#
# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all().order_by('name')
#     serializer_class = GroupSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#
# def keking(request):
#     data = {'users': ['Zaychal', 'Kozlyazh', 'Kotedral1']}
#     return JsonResponse(data)
#
#
# @api_view(['GET', 'POST'])
# def my_api_view(request):
#     if request.method == 'GET':
#         return Response({"message": "Это GET запрос!"}, status=status.HTTP_200_OK)
#     elif request.method == 'POST':
#         data = request.data  # DRF автоматически парсит JSON
#         return Response({"received_data": data}, status=status.HTTP_201_CREATED)
#
#
# class MyAPIView(APIView):
#     # permission_classes = [permissions.IsAuthenticated]
#     queryset = User.objects.all()
#
#     def get(self, request):
#         return Response({"message": "Это GET запрос!"}, status=status.HTTP_200_OK)
#
#     def post(self, request):
#         data = request.data
#         return Response({"received_data": data}, status=status.HTTP_201_CREATED)
#
#
# class SnippetViewSet(viewsets.ModelViewSet):
#     """
#     This ViewSet automatically provides `list`, `create`, `retrieve`,
#     `update` and `destroy` actions.
#
#     Additionally we also provide an extra `highlight` action.
#     """
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly,
#                           IsOwnerOrReadOnly] #permissions.IsAuthenticated,
#
#     @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
#     def highlight(self, request, *args, **kwargs):
#         snippet = self.get_object()
#         return Response(snippet.highlighted)
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)
#
#
# # tutor 5
# @api_view(['GET'])
# def api_root(request, format=None):
#     print('api trigger')
#     return Response({
#         'users': reverse('user-list', request=request, format=format),
#         'snippets': reverse('snippet-list', request=request, format=format)
#     })
