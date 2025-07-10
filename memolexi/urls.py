"""
URL configuration for memolexi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from memo import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# router = DefaultRouter()
# router.register(r'words', views.Wording, basename='wordcards')  # Обратите внимание на имя
# router.register(r'users', views.UserListView, basename='user')
# router.register(r'parts-of-speech', views.PartOfSpeechViewSet, basename='partofspeech')  # Новый маршрут


urlpatterns = [
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/', include('rest_framework.urls')),
    
    path('users/', views.UserListView.as_view(), name='users-list'),
    path('words/<int:pk>/', views.WordDetail.as_view(), name='words-detail'),
    path('words/upload/', views.UploadWordsView.as_view()),  # uw/  api/upload-words
    path('words/', views.WordListView.as_view(), name='words-list'),
    
    path('srs/', views.SRSessionView.as_view(), name='spaced-repetition-system'),
    
    path('', include('users.urls')),
] + debug_toolbar_urls()  # + router.urls)


"""Второй вариант"""
# router = routers.DefaultRouter()
# # router = routers.SimpleRouter()
# router.register(r'snippets', views.SnippetViewSet, basename='snippet')
# router.register(r'users', views.UserViewSet, basename='user')
#
# # The API URLs are now determined automatically by the router.
# urlpatterns = [
#     path('', include(router.urls)),
#     path('api-auth/', include('rest_framework.urls')),
#     path('api/', views.api_root),  # Добавление маршрута для api_root
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
# ]

"""Первый вариант"""
# urlpatterns = format_suffix_patterns([
#     path('', views.api_root),
#     path('kek/', views.keking),
#     path('testing/', views.MyAPIView.as_view()),
#     path('testing1/', views.my_api_view),
# ])


# snippet_list = SnippetViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })
# snippet_detail = SnippetViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })
# snippet_highlight = SnippetViewSet.as_view({
#     'get': 'highlight'
# }, renderer_classes=[renderers.StaticHTMLRenderer])
# user_list = UserViewSet.as_view({
#     'get': 'list'
# })
# user_detail = UserViewSet.as_view({
#     'get': 'retrieve'
# })
#
#
# # Wire up our API using automatic URL routing.
# # Additionally, we include login URLs for the browsable API.
# urlpatterns = format_suffix_patterns([
#     path('', views.api_root),
#     path('kek/', views.keking),
#     path('testing/', views.MyAPIView.as_view()),
#     path('testing1/', views.my_api_view),
#
#     path('', api_root),
#     path('snippets/', snippet_list, name='snippet-list'),
#     path('snippets/<int:pk>/', snippet_detail, name='snippet-detail'),
#     path('snippets/<int:pk>/highlight/', snippet_highlight, name='snippet-highlight'),
#     path('users/', user_list, name='user-list'),
#     path('users/<int:pk>/', user_detail, name='user-detail')
# ])
