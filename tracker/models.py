from django.db import models
from django.conf import settings

from .validators import (
    validate_habit,
    validate_duration_seconds_value,
    validate_period_days_value,
)


class Habit(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='habits', on_delete=models.CASCADE)
    action = models.CharField(max_length=300)
    place = models.CharField(max_length=200, blank=True)
    time_of_day = models.TimeField(null=True, blank=True)

    is_pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='related_to')
    reward = models.CharField(max_length=300, blank=True)

    period_days = models.PositiveIntegerField(
        default=1,
        validators=[validate_period_days_value],
        help_text='Периодичность выполнения привычки в днях (от 1 до 7)'
    )
    duration_seconds = models.PositiveIntegerField(
        default=60,
        validators=[validate_duration_seconds_value],
        help_text='Время выполнения привычки в секундах (не более 120)'
    )

    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        """Валидация модели через отдельные валидаторы"""
        validate_habit(self)

    def save(self, *args, **kwargs):
        """Валидация будет выполняться всегда, независимо от источника данных"""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Я буду {self.action} в {self.time_of_day or 'любое время'} в {self.place}."


