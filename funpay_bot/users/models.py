import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    telegram_chat_id = models.IntegerField(unique=True)
    subscribe_time = models.DateTimeField(
        default=datetime.datetime.now() + datetime.timedelta(days=3))

    USERNAME_FIELD = 'telegram_chat_id'

    def __str__(self):
        return f'{self.telegram_chat_id}'
