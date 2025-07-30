from django.test import TestCase

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
# from .models import Snippet


class SnippetAPITestCase(APITestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
        # Указываем URL для создания Snippet
        self.url = '/snippets/'

    # def test_create_snippet(self):
    #     # Данные для создания нового Snippet
    #     data = {
    #         "title": "Test Snippet",
    #         "code": """def test_create_snippet(self):
    #     # Данные для создания нового Snippet
    #     data = {
    #         "title": "Test Snippet",
    #         "code": "print('Hello, world!')",
    #     }
    #     response = self.client.post(self.url, data)""",
    #     }
    #     response = self.client.post(self.url, data)
    #
    #     # Проверяем статус ответа
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    #     # Проверяем, что объект действительно создан
    #     self.assertEqual(Snippet.objects.count(), 1)
    #     self.assertEqual(Snippet.objects.first().title, "Test Snippet")
