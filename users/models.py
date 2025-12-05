from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    main_language = models.ForeignKey('references.Language', on_delete=models.SET_NULL, null=True,
                                      blank=True, related_name='users_with_main_language')
    
    # Переопределяю поля, чтобы не было конфликта с auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',  # ← любое уникальное
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # ← то же самое
    )
    
    def __str__(self):
        return self.username
    