from rest_framework import serializers
from memo.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES
from django.contrib.auth.models import Group, User


class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = ['id', 'created', 'title', 'code', 'linenos', 'language', 'style']
    
    def create(self, validated_data):
        # Добавляем текущего пользователя из context в данные
        a = self.context
        print(a)
        # if self.context['request'].user:
        #     validated_data['owner'] = self.context['request'].user
        # else:
        #     validated_data['owner'] = 'UNknown'
        return super().create(validated_data)
    

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
        