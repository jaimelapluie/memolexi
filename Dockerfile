#  Python образ
FROM python:3.13-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем все файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Указываем команду по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
