from django.core.exceptions import ValidationError


def validate_not_empty(value):
    if not value.strip():
        raise ValidationError("Название не может быть пустым !")
    