from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from memo.models import Snippet
from memo.permissions import IsOwnerOrReadOnly
from memo.serializers import SnippetSerializer, UserSerializer, GroupSerializer
from django.http import JsonResponse, Http404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status


# import os
# print("PATH:", os.environ.get("PATH"))
# import psycopg2
# print("Psycopg2 version:", psycopg2.__version__)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
 

def keking(request):
    data = {'users': ['Zaychal', 'Kozlyazh', 'Kotedral1']}
    return JsonResponse(data)


# @api_view(['GET', 'POST'])
# def my_api_view(request):
#     data = {'users': ['user22', 'user33', 'admin1']}
#     return JsonResponse(data)

@api_view(['GET', 'POST'])
def my_api_view(request):
    if request.method == 'GET':
        return Response({"message": "Это GET запрос!"}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        data = request.data  # DRF автоматически парсит JSON
        return Response({"received_data": data}, status=status.HTTP_201_CREATED)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class MyAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    
    def get(self, request):
        return Response({"message": "Это GET запрос!"}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        return Response({"received_data": data}, status=status.HTTP_201_CREATED)


class SnippetList(generics.ListCreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        print('A_perform_create')
        serializer.save(owner=self.request.user)


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                      IsOwnerOrReadOnly]
    

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
