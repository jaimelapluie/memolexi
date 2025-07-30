from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    main_language = models.CharField(max_length=15, blank=True, null=True)
    