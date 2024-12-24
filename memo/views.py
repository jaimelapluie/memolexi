from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from rest_framework.permissions import AllowAny

from memo.models import Snippet
from memo.serializers import SnippetSerializer, UserSerializer, GroupSerializer
from django.http import JsonResponse, Http404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status


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
    data = {'users': ['Zaychal', 'Kozlyazh', 'Kotedral']}
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


class SnippetList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SnippetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class SnippetDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self, pk):
        try:
            return Snippet.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)