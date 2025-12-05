from django.db import models
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model

from common.validators import validate_not_empty
from common import constants

User = get_user_model()

# from pygments.lexers import get_all_lexers
# from pygments.styles import get_all_styles
# from pygments import highlight
# from pygments.formatters.html import HtmlFormatter
# from pygments.lexers import get_lexer_by_name

# from memo.services import SM2Algorithm
# SM2Algorithm

# LEXERS = [item for item in get_all_lexers() if item[1]]
# LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
# STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])


# class Snippet(models.Model):
#     created = models.DateTimeField(auto_now_add=True)
#     title = models.CharField(max_length=100, blank=True, default='')
#     code = models.TextField()
#     linenos = models.BooleanField(default=False)
#     language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
#     style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)
#     owner = models.ForeignKey('auth.User', related_name='snippets',
#                               on_delete=models.CASCADE, null=True, blank=True)
#     highlighted = models.TextField()
#
#     class Meta:
#         ordering = ['created']
#
#     def save(self, *args, **kwargs):
#         """
#         Use the `pygments` library to create a highlighted HTML
#         representation of the code snippet.
#         """
#         lexer = get_lexer_by_name(self.language)
#         linenos = 'table' if self.linenos else False
#         options = {'title': self.title} if self.title else {}
#         formatter = HtmlFormatter(style=self.style, linenos=linenos,
#                                   full=True, **options)
#         self.highlighted = highlight(self.code, lexer, formatter)
#         super().save(*args, **kwargs)


class WordCards(models.Model):
    word = models.CharField(max_length=255, blank=True, null=True, default=None)
    translation = models.TextField(max_length=3000, blank=True, null=True)
    example = models.TextField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=300, blank=True, null=True)
    reverso_url = models.CharField(max_length=300, blank=True, null=True)
    picture = models.ImageField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='words')
    time_create = models.DateTimeField(auto_now_add=True)
    part_of_speech = models.ForeignKey('references.PartOfSpeech', blank=True, null=True,
                                       on_delete=models.PROTECT, related_name='words')
    language = models.ForeignKey('references.Language', on_delete=models.SET_NULL, null=True,
                                 blank=True, related_name='words')
    
    # Spaced Repetition System Params
    interval_days = models.PositiveIntegerField(default=1)
    repetition_level = models.PositiveIntegerField(default=1)
    easiness_factor = models.FloatField(default=2.5)
    next_review = models.DateField(default=datetime.today)
    
    def __str__(self):
        return self.word or "Без названия"
    # from memo.views import WordCards as wc
    # q = wc.objects.all()
    
    class Meta:
        ordering = ['-time_create']
        verbose_name = "Карточка слова"
        verbose_name_plural = "Карточки слов"
    
    def calculate_next_review(self, word_instance, quality):
        """
        Обновляет интервалы повторения слова по алгоритму SM-2.

        :param word_instance: экземпляр модели WordCards
        :param quality: оценка от 0 до 5

        interval_days = models.PositiveIntegerField(default=1)
        repetition_level = models.PositiveIntegerField(default=1)
        easiness_factor = models.FloatField(default=2.5)
        next_review = models.DateField(default=datetime.today)
        """
        
        easiness_factor = max(
            constants.MIN_Easiness_Factor,
            word_instance.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        )
        
        if quality < 3:
            repetition_level = 1
            interval_days = 1
        else:
            if word_instance.repetition_level == 1:
                interval_days = 1
            elif word_instance.repetition_level == 2:
                interval_days = 6
            else:
                interval_days = round(word_instance.interval_days * easiness_factor)
            repetition_level = word_instance.repetition_level + 1
        
        word_instance.interval_days = interval_days
        word_instance.repetition_level = repetition_level
        word_instance.easiness_factor = easiness_factor
        word_instance.next_review = datetime.now().date() + timedelta(days=interval_days)


class ReviewHistory(models.Model):
    word_card = models.ForeignKey("WordCards", on_delete=models.CASCADE, related_name="reviews")
    reviewed_at = models.DateTimeField(auto_now_add=True)
    quality = models.IntegerField()  # Оценка от 0 до 5
    interval_days = models.IntegerField()  # Интервал после ответа
    easiness_factor = models.FloatField()  # EF после ответа
    repetition_level = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.word_card.word} - Оценка: {self.quality}"
    
    class Meta:
        ordering = ['-reviewed_at']
        verbose_name = "История повторения"
        verbose_name_plural = "История повторений"
        

class WordCardsList(models.Model):
    word_card = models.ForeignKey('WordCards', on_delete=models.CASCADE, related_name='wordcards_links')
    word_lists = models.ForeignKey('WordList', on_delete=models.CASCADE, blank=True, default=None, null=True,
                                   related_name='wordlists_links')
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        # return f"{self.word_card.word} —> {self.topic.name}"
        return f"{self.word_card} —> {self.word_lists}"
    
    class Meta:
        verbose_name = "Связь карточки и списка со словами"
        verbose_name_plural = "Связь карточек и списков со словами"
    
    
class WordList(models.Model):
    name = models.CharField(max_length=255, validators=[validate_not_empty])
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='word_lists')

    def __str__(self):
        return f"{self.name} created by {self.author}"

    class Meta:
        verbose_name = "Список слов"
        verbose_name_plural = "Списки слов"
        unique_together = ('name', 'author')
