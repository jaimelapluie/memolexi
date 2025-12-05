from django.db import models

from common.validators import validate_not_empty


class PartOfSpeech(models.Model):
    part_of_speech = models.CharField(max_length=50, unique=True, validators=[validate_not_empty])
    
    def __str__(self):
        return self.part_of_speech
    
    class Meta:
        verbose_name = "Часть речи"
        verbose_name_plural = "Части речи"


class Language(models.Model):
    code = models.CharField(max_length=7, unique=True)
    name = models.CharField(max_length=15, unique=True)
    name_native = models.CharField(max_length=15, blank=True)
    flag_emoji = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return f"{self.flag_emoji}{self.name}" if self.flag_emoji else self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Язык"
        verbose_name_plural = "Языки"
