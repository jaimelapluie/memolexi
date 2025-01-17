from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name

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


def validate_not_empty(value):
    if not value.strip():
        raise ValidationError("Название не может быть пустым !")
    
    
class WordCards(models.Model):
    word = models.CharField(max_length=255, validators=[validate_not_empty])
    translation = models.TextField(max_length=3000, blank=True, null=True)
    example = models.TextField(max_length=255, blank=True, null=True)
    picture = models.ImageField(blank=True, null=True)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, related_name='words')
    time_create = models.DateTimeField(auto_now_add=True)
    part_of_speech = models.ForeignKey('PartOfSpeech', blank=True, on_delete=models.PROTECT, related_name='words')
    
    def __str__(self):
        return self.word
    
    class Meta:
        ordering = ['-time_create']
        verbose_name = "Карточка слова"
        verbose_name_plural = "Карточки слов"


class WordCardsTopic(models.Model):
    word_card = models.ForeignKey('WordCards', on_delete=models.CASCADE, related_name='word_topics')
    topics = models.ForeignKey('Topic', on_delete=models.CASCADE, blank=True, related_name='word_topics')
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        # return f"{self.word_card.word} —> {self.topic.name}"
        return f"{self.word_card} —> {self.topics}"
    
    class Meta:
        verbose_name = "Связь карточки и темы"
        verbose_name_plural = "Связь карточек и тем"
    
    
class Topic(models.Model):
    name = models.CharField(max_length=255, validators=[validate_not_empty])
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, related_name='topics')

    def __str__(self):
        return f"{self.name} created by {self.author}"

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"
        unique_together = ('name', 'author')
        
        
class PartOfSpeech(models.Model):
    part_of_speech = models.CharField(max_length=50, null=True, default=None, validators=[validate_not_empty])
    
    def __str__(self):
        return self.part_of_speech

    class Meta:
        verbose_name = "Часть речи"
        verbose_name_plural = "Части речи"
