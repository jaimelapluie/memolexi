from rest_framework import serializers


from memo.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES
from django.contrib.auth.models import Group, User


class SnippetSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Snippet
        fields = ['id', 'created', 'title', 'code', 'linenos', 'language', 'style', 'owner', ] #'highlighted'
    
    def create(self, validated_data):
        # Добавляем текущего пользователя из context в данные
        a = self.context
        print('!!!', a)
        if 'request' in self.context and self.context['request'].user and \
            not self.context['request'].user.is_anonymous:
            validated_data['owner'] = self.context['request'].user
        else:
            validated_data['owner'] = None
        return super().create(validated_data)
    

class UserSerializer(serializers.ModelSerializer):
    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'snippets']
        
        
class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
        