from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, serializers
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from memo.filters import WordFilter1, WordFilter2, CustomOrderingFilter
from memo.models import WordCards, PartOfSpeech, WordCardsList, ReviewHistory  # Snippet
from memo.paginations import CustomPageNumberPagination, CastomLimitOffsetPagination
from memo.permissions import IsOwnerOrReadOnly
from memo.serializers import WordSerializer, WordReviewSerializer  # SnippetSerializer, GroupSerializer
from users.serializers import UserSerializer

from django.http import JsonResponse, Http404

from rest_framework.decorators import api_view, authentication_classes

from rest_framework.reverse import reverse
from rest_framework import renderers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from memo.services import WordService
from memo.tasks.word_transfer import WordTransfer
from datetime import timedelta, datetime
from django.utils.timezone import now


class WordDetail(APIView):
    permission_classes = [IsAuthenticated]  # [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    
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


# @authentication_classes([SessionAuthentication, ])  # BasicAuthentication
class WordListView(APIView):
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = WordFilter2
    
    # filter_backends = [WordFilter1, CustomOrderingFilter]
    filter_backends = [CustomOrderingFilter]
    ordering_fields = ['word', 'translation', 'time_create', 'length']
    
    pagination_class = CastomLimitOffsetPagination  # CustomPageNumberPagination
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]  # [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    
    def get(self, request):
        # queryset = (WordCards.objects
        #             .select_related('part_of_speech')
        #             .prefetch_related('wordcards_links__word_lists')
        #             .all())
        print(request.user)
        queryset = (
            WordCards.objects.select_related("part_of_speech")
            .prefetch_related(
                Prefetch(  # Перечитать как нюансы как это работает
                    "wordcards_links",
                    queryset=WordCardsList.objects.select_related("word_lists").only(
                        "word_lists__name", "word_lists__author"
                    ),
                )
            )
            .all()
        )
        
        # Применяем фильтры
        for beckend_instance in self.filter_backends:
            print('for beckend_instance in self.filter_backends ...')
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
                return Response({"error_from WordListView.post": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            if created:
                print('wording/post зашел')
                return Response(WordSerializer(word).data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'message': f'{serializer.validated_data.get("word")} is already exists'},
                    status=status.HTTP_409_CONFLICT
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckUsernameView(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        if not username:
            return Response({"error": "username isn't provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        exists = get_user_model().objects.filter(username=username).exists()
        print(f'CheckUsernameView(APIView): проверка наличия if not username: {exists}')
        return Response({"exists": exists})


class CheckTelegramIdView(APIView):
    def get(self, request):
        telegram_id = request.query_params.get("telegram_id")
        print(f"CheckTelegramIdView - telegram_id = {telegram_id}")
        try:
            finded_user_profile = get_user_model().objects.get(telegram_id=telegram_id)
            print(finded_user_profile)
            print(type(finded_user_profile))
            serializer = UserSerializer(finded_user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except get_user_model().DoesNotExist:
            return Response({"service message": f"Пользователь с telegram_id {telegram_id} не был найден"},
                            status=status.HTTP_404_NOT_FOUND)

    
class UserListView(APIView):
    def get(self, request):
        usernames = get_user_model().objects.all()
        serializer = UserSerializer(usernames, many=True)
        print('A', type(usernames), usernames)
        print('B----')
        print(serializer)
        print('C----')
        [print(serializer.data[0]) if len(serializer.data) else ""]
        # return JsonResponse(serializer.data, safe=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):  # {"username": "kek"}
        serializer = UserSerializer(data=request.data)
        print(f"serializer={serializer}")
        print(f"request.data= {request.data}")
        # if serializer.is_valid():
        #     try:
        #         # Если записи нет, создаём новую
        #         print('serializer.validated_data', serializer.validated_data)
        #         print('Проверка идеи', serializer.validated_data['username'])
        #         password = validated_data.pop("password", None)
        #         # Создаю пользователя без пароля
        #         user = self.Meta.model()(**validated_data)
        #         # Устанавливаю пароль с хэшированием
        #         if password is not None:
        #             user.set_password(password)
        #         user.save()
        #         author, created = get_user_model().objects.get_or_create(**serializer.validated_data)
        #         print(author, created)
        #     except Exception as e:
        #         return Response({"error_from UserListView.post": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        #
        #     if created:
        #         print('UserListView/post/created зашел')
        #         print(f"type(author)={type(author)}")
        #         print(f"UserSerializer(author).data={UserSerializer(author).data}")
        #         print(f"type(UserSerializer(author).data)={type(UserSerializer(author).data)}")
        #         return Response(UserSerializer(author).data, status=status.HTTP_201_CREATED)
        #     else:
        #         return Response(
        #             {'message': f'"{serializer.validated_data.get(author)}" is already exists'},
        #             status=status.HTTP_409_CONFLICT
        #         )
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            try:
                username = serializer.validated_data.get('username')
                user_exists = get_user_model().objects.filter(username=username).exists()
                print(username, user_exists)
                if user_exists:
                    print("Зашел в UserListView в if user_exists ")
                    return Response({'message': f'"{serializer.validated_data.get(username)}" is already exists'},
                                    status=status.HTTP_409_CONFLICT)
                user = serializer.save()
                
                return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            except Exception as err:
                return Response({"error_from UserListView.post": str(err)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):  # сделать доступ по токену
    def put(self, request):
        print("UserDetailView -> put")
        print(request)
        print(request.query_params)
        username = request.query_params.get('username')
        telegram_id = request.query_params.get('telegram_id')
        
        if not username and not telegram_id:
            return Response({"service message": "Должен быть передан username или telegram_id"},
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if username:
                user = get_user_model().objects.get(username=username)
            elif telegram_id:
                user = get_user_model().objects.get(telegram_id=telegram_id)
        except get_user_model().DoesNotExist:
            return Response({"service message": "Пользователь не найден"},
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(APIView):
    authentication_classes = [
        JWTAuthentication,
        SessionAuthentication,
        BasicAuthentication
    ]
    
    def delete(self, request):
        user = request.user
        if user.is_anonymous:
            return Response({"service message": "Анонимус, залогинься"},
                            status=status.HTTP_404_NOT_FOUND)
        
        try:
            user.delete()
            return Response({"service message": "Аккаунт удалён"})
        except get_user_model().DoesNotExist as err:
            return Response({"service message": "Пользователь не найден"},
                            status=status.HTTP_404_NOT_FOUND)
    
    
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
            print('UploadWordsView/post', word)
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
                    return Response({"error_from WordListView.post": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
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


class SRSessionView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    
    def get(self, request):
        """
        Возвращает список слов, которые нужно повторить
        """
        queryset = (WordCards.objects.select_related('author')
                    .filter(author=request.user, next_review__lte=now())
                    .order_by("next_review"))[:10]
        serializer = WordSerializer(queryset, many=True)
        return Response({'words': serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        """
        Обновляет интервалы повторения на основе оценок
        Пример запроса:
        [
            {"id": 4, "quality": 1},
            {"id": 5, "quality": 1},
            {"id": 6, "quality": 1}
        ]
        
        [
    {"id": 7, "quality": 3},
    {"id": 8, "quality": 3},
    {"id": 9, "quality": 3},
    {"id": 10, "quality": 3},
    {"id": 11, "quality": 3},
    {"id": 12, "quality": 3},
    {"id": 13, "quality": 3},
    {"id": 14, "quality": 3},
    {"id": 15, "quality": 3},
    {"id": 16, "quality": 3}
]
        """
        # Получаем все объекты, которые пришли в запросе
        ids = [item["id"] for item in request.data]
        queryset = WordCards.objects.filter(id__in=ids, author=request.user)
        
        serializer = WordReviewSerializer(queryset, data=request.data, many=True, context={'user': request.user})
        print('___!')
        print(type(serializer))
        print(type(serializer.child))
        print('___!')
        
        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save()
            return Response({"status": "Words has been updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# {"link": "D:\Obsidian_notes\jaime\English\Vocab_Memolexi — копия.md"}
# {"link": "D:\\Obsidian_notes\\jaime\\English\\Vocab_Memolexi — копия.md"}
