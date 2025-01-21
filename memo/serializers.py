# from memo.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES
from django.contrib.auth.models import Group, User
from memo.models import WordCards
from rest_framework import serializers

import os
"""from rest_framework import serializers
from datetime import datetime
from django.conf import settings

settings.configure(
    INSTALLED_APPS=[
        'rest_framework',
    ]
)


class Comment:
    def __init__(self, email, content, created=None):
        self.email = email
        self.content = content
        self.created = created or datetime.now()

comment = Comment(email='leila@example.com', content='foo bar')


class CommentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField()
    

serializer = CommentSerializer(comment)
a = serializer.data
print('A', type(a), a)

from rest_framework.renderers import JSONRenderer

json = JSONRenderer().render(serializer.data)
print('B', type(json), json)


import io
from rest_framework.parsers import JSONParser

stream = io.BytesIO(json)
data = JSONParser().parse(stream)


serializer = CommentSerializer(data=data)
print('C', serializer.is_valid())
# True
res = serializer.validated_data
print('D', type(res))
print('E', res)"""


# class SnippetSerializer(serializers.ModelSerializer):
#     owner = serializers.ReadOnlyField(source='owner.username')
#
#     class Meta:
#         model = Snippet
#         fields = ['id', 'created', 'title', 'code', 'linenos', 'language', 'style', 'owner', ] #'highlighted'
#
#     def create(self, validated_data):
#         # Добавляем текущего пользователя из context в данные
#         a = self.context
#         print('!!!', a)
#         if 'request' in self.context and self.context['request'].user and \
#             not self.context['request'].user.is_anonymous:
#             validated_data['owner'] = self.context['request'].user
#         else:
#             validated_data['owner'] = None
#         return super().create(validated_data)


# class UserSerializer(serializers.ModelSerializer):
#     snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())
#
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'snippets']

# class SnippetSerializer(serializers.HyperlinkedModelSerializer):
#     owner = serializers.ReadOnlyField(source='owner.username')
#     # owner = serializers.HyperlinkedIdentityField(view_name='user-detail')
#     highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')
#
#     class Meta:
#         model = Snippet
#         fields = ['url', 'id', 'highlight', 'owner',
#                   'title', 'code', 'linenos', 'language', 'style']
#
#
# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippet-detail', read_only=True)
#
#     class Meta:
#         model = User
#         fields = ['url', 'id', 'username', 'snippets']
#
#
# class GroupSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Group
#         fields = ['url', 'name']
"""

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", 'url']


# us1 = User.objects.get(pk=1)
# print('A', us1)
# serializer = UserSerializer(us1)
# print(serializer.is_valid())
# res = serializer.data
# print('B', type(res), res)
#
# from rest_framework.renderers import JSONRenderer
#
# json = JSONRenderer().render(res)
# print('C', json)


class WordSerializer(serializers.HyperlinkedModelSerializer):  #  ModelSerializer):  #
    author = serializers.HyperlinkedRelatedField(many=True, view_name='WordCards-detail', read_only=True)
    # author = UserSerializer(read_only=True)
    
    class Meta:
        model = WordCards
        fields = ["id", "word", "translation", "example", "picture", "time_create", "author", "part_of_speech"]
    
    
# class WordSerializer(serializers.Serializer):
#     word = serializers.CharField(max_length=255)
#     translation = serializers.CharField()
#     example = serializers.CharField()
#     picture = serializers.ImageField()
#     author = serializers.CharField()
#     time_create = serializers.DateTimeField()
#     part_of_speech = serializers.CharField()
    # part_of_speech = serializers.ForeignKey('PartOfSpeech', on_delete=models.PROTECT)
    
        """


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username",]


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordCards
        fields = ["id", "word", "translation", "example", "source", "reverso_url", "picture", "time_create", "author", "part_of_speech"]


class SimpleTransferSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=255)
    translation = serializers.CharField()
    example = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    picture = serializers.ImageField(required=False, allow_null=True)
    author = serializers.CharField(required=False)
    # time_create = serializers.DateTimeField()
    source = serializers.CharField(required=False, allow_null=True)
    reverso_url = serializers.CharField(required=False, allow_null=True)
    # part_of_speech = serializers.CharField()


f = {'word': 'mention', 'translation': 'упомянуть', 'example': 'Other notab', 'source': '[youtube.com]', 'reverso_url': 'reverso'}
