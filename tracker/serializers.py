from rest_framework import serializers
from .models import Habit
from django.contrib.auth import get_user_model


User = get_user_model()

class HabitSerializer(serializers.ModelSerializer):
    # меняет формат вывода владельца (не id а email)
    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Habit
        fields = ['id', 'owner', 'action', 'place', 'time_of_day', 'is_pleasant', 'related_habit',
                  'reward', 'period_days', 'duration_seconds', 'is_public', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'owner']

