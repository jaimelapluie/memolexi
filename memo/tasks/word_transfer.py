# from django.conf import settings
#
# settings.configure(
#     INSTALLED_APPS=[
#         'django.contrib.admin',
#         'django.contrib.auth',
#         'django.contrib.contenttypes',
#         'django.contrib.sessions',
#         'django.contrib.messages',
#         'django.contrib.staticfiles',
#         'rest_framework',
#         'django_filters',
#         'memo',
#     ]
# )
#
# import django
#
# django.setup()  # This line is crucial
# from memo.serializers import WordSerializer, SimpleTransferSerializer


class WordTransfer:
    DEFAULT_FILE_PATH = r"D:\Obsidian_notes\jaime\English\Vocab_Memolexi.md"
    KEYS = ['word', 'translation', 'example', 'source', 'reverso_url']

    def __init__(self, link_source: str = None):
        self.link_source = link_source or self.DEFAULT_FILE_PATH

    def _read_file(self):
        """Читает файл и возвращает строки."""
        try:
            with open(self.link_source, mode='r', encoding='utf-8') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {self.link_source}")
        except Exception as e:
            raise RuntimeError(f"Ошибка при чтении файла: {e}")

    def _parse_snippet(self, snippet):
        """Парсит один блок слов."""
        word_data = dict.fromkeys(self.KEYS, None)

        for i, line in enumerate(snippet):
            if i == 0:  # Парсим слово и URL
                closed_figure_index = line.find(']')
                word_data['word'] = line[1:closed_figure_index]
                word_data['reverso_url'] = line[line.find('(') + 1:-1]
            elif i == 1:  # Парсим перевод
                word_data['translation'] = line
            elif i == 2:  # Парсим пример
                word_data['example'] = line
            elif i == 3:  # Парсим либо источник, либо перевод примера
                if line.startswith('['):  # Источник
                    word_data['source'] = line
                else:  # Перевод примера
                    word_data['example'] += f" ({line})"

        return word_data

    def parser(self) -> list:
        """Основной метод парсинга"""
        lines = self._read_file()
        result = []
        snippet = []

        for line in lines:
            if line != 'enru':
                snippet.append(line)
            else:
                if snippet:
                    result.append(self._parse_snippet(snippet))
                    snippet = []
        print('WordTransfer/parser', type(result), result)
        return result


# words = WordTransfer().parser()
# print(words)

# print(*words, sep='\n')
# print(len(words))


# res = SimpleTransferSerializer(data=words, many=True)  # words, many=True)  #
# res = WordSerializer(data=words, many=True)
# print(res.is_valid())
# print(res.errors)
# print(res.validated_data)
# res.save()


# from rest_framework.renderers import JSONRenderer
#
# "Преобразуем сериализованные данные в JSON"
# json = JSONRenderer().render(words)
# print('B', type(json), json)
# # B <class 'bytes'> b'{"email":"leila@example.com","content":"foo bar","created":"2025-01-10T15:13:45.061464-06:00"}'
#
# import io
# from rest_framework.parsers import JSONParser
#
# "Преобразуем байтовый поток JSON обратно в Python словарь"
# stream = io.BytesIO(json)
# data = JSONParser().parse(stream)
#
# "Из потока байт"
# serializer = WordSerializer(data=data)  # Создаем новый сериализатор с входящими данными
# print('C', serializer.is_valid())  # Проверяем валидность данных
# # C True
#
# res = serializer.validated_data  # Получаем валидированные данные
# print('D', type(res))
# # D <class 'dict'>
#
# print('E', res)
