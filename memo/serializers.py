# from memo.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES
from django.contrib.auth.models import Group, User
from memo.models import WordCards, PartOfSpeech, WordCardsList, WordList, ReviewHistory
from rest_framework import serializers

from django.utils.timezone import now
import os

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


class WordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordList
        fields = ["name", "author"]


class WordCardsListSerializer(serializers.ModelSerializer):
    word_lists = WordListSerializer()
    
    class Meta:
        model = WordCardsList
        fields = ["word_lists"]


class WordSerializer(serializers.ModelSerializer):
    part_of_speech = serializers.CharField(source='part_of_speech.part_of_speech', read_only=True, required=False)
    # word_lists = serializers.ListField(
    #     child=serializers.CharField(),
    #     source='wordcards_links.values_list("word_lists__name", flat=True)',
    #     read_only=True
    # )
    word_lists = serializers.SerializerMethodField()
    author = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = WordCards
        fields = ["id", "word", "translation", "example", "source", "reverso_url", "picture", "time_create",
                  "author", "part_of_speech", "word_lists"]
        read_only_fields = ["word_lists"]  # Указываем, что поле только для чтения
    
    def get_word_lists(self, obj):
        print('>get_word_lists>', type(obj), obj)
        return list(obj.wordcards_links.values_list("word_lists__name", flat=True))
    
    
class PartOfSpeechSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartOfSpeech
        fields = ["part_of_speech"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", ]


class WordReviewListSerializer(serializers.ListSerializer):
    def update(self, instance_list, validated_data):
        instance_mapping = {instance.id: instance for instance in instance_list}
        review_history = []
        
        for item in validated_data:  # ПОСМОТРЕТЬ КАК ВЫГЛЯДИТ validated_data  [{'id': 1, 'val': 5 }, { } ]
            word = instance_mapping.get(item['id'])
            quality = item['quality']
            
            if word:
                word.calculate_next_review(word, quality)
                
                review_history.append(
                    ReviewHistory(
                        word_card=word,
                        reviewed_at=now(),
                        quality=quality,
                        interval_days=word.interval_days,
                        easiness_factor=word.easiness_factor,
                        repetition_level=word.repetition_level
                        
                    )
                )
        
        WordCards.objects.bulk_update(instance_list,
                                      ['next_review', 'interval_days', 'easiness_factor', 'repetition_level'])
        ReviewHistory.objects.bulk_create(review_history)
        return instance_list
    
    def create(self, validated_data):
        print('kek?')
        return self
    
    
class WordReviewSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    quality = serializers.IntegerField(required=True, min_value=0, max_value=5)
    
    class Meta:
        model = WordCards
        fields = ['id', 'quality', ]
        list_serializer_class = WordReviewListSerializer
    
    @classmethod
    def many_init(cls, *args, **kwargs):
        # 1. Создаем экземпляр сериализатора для одного объекта
        # cls() = WordReviewSerializer()
        kwargs['child'] = cls()
        
        # 2. Возвращаем экземпляр кастомного ListSerializer с этим child
        # args и kwargs передаются в WordReviewListSerializer.__init__
        return WordReviewListSerializer(*args, **kwargs)
    

# class WordReviewSerializer(serializers.ModelSerializer):
#     quality = serializers.IntegerField(write_only=True, min_value=0, max_value=5)
#
#     class Meta:
#         model = WordCards
#         fields = ["id", "word", "translation", "quality"]
