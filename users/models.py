from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    tg_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Телеграм chat-id"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

