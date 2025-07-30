from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (RegisterSerializer, DeleteAccountSerializer, ChangePasswordSerializer,
                          PasswordResetSerializer, SetNewPasswordSerializer)
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
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


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    
    def post(self, request):
        user = request.user
        if not user.check_password(request.data.get('old_password')):
            return Response({"error": "Неверный текущий пароль"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data.get('new_password')
            user.set_password(new_password)
            user.save()
            
            return Response({"message": "Пароль успешно изменен"}, status=status.HTTP_200_OK)
        return Response({**serializer.errors, "message": "non valid"}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Отправка email со ссылкой для сброса пароля
    """
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = get_user_model().objects.filter(email=email).first()
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))  # Кодирую ID пользователя
                token = default_token_generator.make_token(user)  # Генерирую токен
                reset_url = f"http://127.0.0.1:8000/api/reset-password/{uid}/{token}/"
                
                # Отправляю email
                send_mail(
                    "Memolexi Password Reset",
                    f"Hi, {user.username}! "
                    f"Password reset was requested. If it was you - follow the link: {reset_url}",
                    "memolexi@memolexi.com",
                    [email],
                    fail_silently=False,
                )
            return Response({"message": "If email exist, we will send a link"},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                

class PasswordResetConfirmView(APIView):
    """
        Позволяет юзеру ввести новый пароль после перехода по ссылке из email
    """
    def post(self, request, uidb64, token):
        try:
            uid = force_bytes(urlsafe_base64_decode(uidb64))  # Декодирую ID
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return Response({"error": "Неверный токен или пользователь не найден"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Проверка токена
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Wrong token"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password was changed"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        