from typing import Any

from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, serializers
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import ModelViewSet

from memo.filters import WordFilter1, WordFilter2
from memo.models import WordCards, PartOfSpeech  # Snippet
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = WordFilter2
    
    def get(self, request):
        queryset = WordCards.objects.all()
        for beckend_instance in self.filter_backends:
            queryset = beckend_instance().filter_queryset(request=request, queryset=queryset, view=self)
        
        serializer = WordSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        serializer = WordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        return Response({"message": "Send me a link to the file with the words "
                                    "or empty request (for using default file)",
                         "Expected format": "key='link': value=<folder link>"},
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
            if not WordCards.objects.filter(
                word=word['word'],
                translation=word['translation'],
                example=word['example']
            ).exists():
                serializer = WordSerializer(data=word)
                if serializer.is_valid():
                    instance = serializer.save()
                    created_words.append(instance)
            else:
                existing_words.append(word['word'])
                
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
