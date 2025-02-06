from django.contrib.auth import get_user_model

from memo.models import WordCards, WordList, WordCardsList


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
            defaults={"author": author}
        )
        print('master_list', master_list, _)
        
        # Связываем слово с master_list
        WordCardsList.objects.get_or_create(word_card=word, word_lists=master_list)
        print('Сервисный', word, created)
        return word, created
    