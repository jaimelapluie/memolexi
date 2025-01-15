from django.contrib import admin
from .models import WordCards, Topic, WordCardsTopic, PartOfSpeech

admin.site.register(WordCards)
admin.site.register(Topic)
admin.site.register(WordCardsTopic)
admin.site.register(PartOfSpeech)
