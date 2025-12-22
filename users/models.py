from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from tracker.models import Habit


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

