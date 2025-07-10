from django.contrib.auth import get_user_model

from memo.models import WordCards, WordList, WordCardsList
from datetime import timedelta, datetime


User = get_user_model()


class WordService:
    @staticmethod
    def create_word_with_master_list(word_data, user=None):
        """
        Создаёт слово и связывает его с master_list.
        :param word_data: Данные для создания слова.
        :param user: Текущий пользователь. Если None, используется администратор.
        """
        # Определяем автора
        author = user if user and user.is_authenticated else User.objects.filter(is_superuser=True).first()
        print('service ->', author)
        
        # создаем слово
        word, created = WordCards.objects.get_or_create(
            word=word_data.get('word'),
            translation=word_data.get('translation'),
            example=word_data.get('example'),
            defaults={**word_data, 'author': author}  # Если записи нет, создаём новую
        )
        print('слово/создано?', word, created)
        
        # Если слово уже существовало и у него нет автора, обновляем поле
        if not created and not word.author:
            WordCards.objects.filter(id=word.id).update(author=author)
        
        # Создаём или получаем master_list с указанным автором
        master_list, _ = WordList.objects.get_or_create(
            name='master_list',
            author=author,
            defaults={"author": author}
        )
        print('master_list', master_list, _)
        
        # Связываем слово с master_list
        WordCardsList.objects.get_or_create(word_card=word, word_lists=master_list)
        print('Сервисный', word, created)
        return word, created


# class SM2Algorithm:  # --> переписать на функцию
#     MIN_Easiness_Factor = 1.3  # Минимальный коэффициент легкости
#
#     @staticmethod
#     def calculate_next_review(word_instance, quality):
#         """
#         Обновляет интервалы повторения слова по алгоритму SM-2.
#
#         :param word_instance: экземпляр модели WordCards
#         :param quality: оценка от 0 до 5
#
#         interval_days = models.PositiveIntegerField(default=1)
#         repetition_level = models.PositiveIntegerField(default=1)
#         easiness_factor = models.FloatField(default=2.5)
#         next_review = models.DateField(default=datetime.today)
#         """
#
#         easiness_factor = max(
#             SM2Algorithm.MIN_Easiness_Factor,
#             word_instance.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
#         )
#
#         if quality < 3:
#             repetition_level = 1
#             interval_days = 1
#         else:
#             if word_instance.repetition_level == 1:
#                 interval_days = 1
#             elif word_instance.repetition_level == 2:
#                 interval_days = 6
#             else:
#                 interval_days = round(word_instance.interval_days * easiness_factor)
#             repetition_level = word_instance.repetition_level + 1
#
#         word_instance.interval_days = interval_days
#         word_instance.repetition_level = repetition_level
#         word_instance.easiness_factor = easiness_factor
#         word_instance.next_review = datetime.now().date() + timedelta(days=interval_days)
        
        # word_instance.save()
        