from memo.models import WordCards, WordCardsList, WordList, ReviewHistory
from rest_framework import serializers

from django.utils.timezone import now

from references.models import Language
from references.serializers import LanguageSerializer


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
    language_code = serializers.CharField(write_only=True, required=False)
    # language = serializers.CharField(source='language.name_native', read_only=True, required=False)
    language = LanguageSerializer(read_only=True)
    word_lists = serializers.SerializerMethodField()
    author = serializers.CharField(source='author.username', read_only=True)
    
    def validate(self, attrs):
        code = attrs.pop("language_code", None)
        if code:
            try:
                attrs["language"] = Language.objects.get(code=code)
            except Language.DoesNotExist:
                raise serializers.ValidationError(
                    {"language_code": "Invalid language code"}
                )
        return attrs
    
    class Meta:
        model = WordCards
        fields = ["id", "word", "translation", "example", "source", "reverso_url", "picture", "time_create",
                  "author", "part_of_speech", "language_code", "language", "word_lists"]
        read_only_fields = ["word_lists",]  # Указываем, что поле только для чтения
        extra_kwargs = {
            "language": {"read_only": True},
        }
    
    def get_word_lists(self, obj):
        print('>get_word_lists>', type(obj), obj)
        return list(obj.wordcards_links.values_list("word_lists__name", flat=True))

 
class WordReviewListSerializer(serializers.ListSerializer):
    def update(self, instance_list, validated_data):
        instance_mapping = {instance.id: instance for instance in instance_list}
        review_history = []
        
        for item in validated_data:
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
