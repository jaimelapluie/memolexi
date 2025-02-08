from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import RegisterSerializer, DeleteAccountSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]

    
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    serializer_class = DeleteAccountSerializer
    parser_classes = [JSONParser]  # Добавляем поддержку JSON-тела в DELETE

    def delete(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data)
            print(request.data)
            if user.check_password(serializer.validated_data.get('password')):
                print('Удолил')
                # user.delete()
                return Response({"message": f"Аккаунт {user.username} удален"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"error": "Неверный пароль"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
