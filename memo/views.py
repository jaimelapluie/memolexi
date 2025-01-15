from typing import Any

from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, serializers
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import ModelViewSet

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
    def get(self, request):
        words = WordCards.objects.all()
        # return Response(list(words.values()))
        serializer = WordSerializer(words, many=True)
        return Response(serializer.data)
    
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
