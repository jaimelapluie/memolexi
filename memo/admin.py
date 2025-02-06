from django.contrib import admin
from .models import WordCards, WordList, WordCardsList, PartOfSpeech

admin.site.register(WordCards)
admin.site.register(WordList)
admin.site.register(WordCardsList)
admin.site.register(PartOfSpeech)
