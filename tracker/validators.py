from django.core.exceptions import ValidationError


class BaseModelValidator:
    """Базовый класс для валидаторов, проверяющих связи между полями модели"""
    error_message = None
    
    def __call__(self, instance):
        if not self.validate(instance):
            raise ValidationError(self.error_message or self.get_error_message(instance))
    
    def validate(self, instance):
        """Метод должен быть переопределен в дочерних классах"""
        raise NotImplementedError
    
    def get_error_message(self, instance):
        """Можно переопределить для динамических сообщений"""
        return self.error_message


def validate_duration_seconds_value(value):
    """Валидатор для поля duration_seconds: время выполнения должно быть не более 120 секунд"""
    if value > 120:
        raise ValidationError('Время выполнения должно быть не более 120 секунд.')
    return value


def validate_period_days_value(value):
    """Валидатор для поля period_days: периодичность должна быть от 1 до 7 дней"""
    if not (1 <= value <= 7):
        raise ValidationError('Периодичность должна быть от 1 до 7 дней.')
    return value


class RewardAndRelatedHabitValidator(BaseModelValidator):
    """Проверка: нельзя указать одновременно вознаграждение и связанную привычку"""
    error_message = 'Укажите только вознаграждение или только приятную привычку.'
    
    def validate(self, habit):
        reward_provided = habit.reward and habit.reward.strip()
        return not (reward_provided and habit.related_habit)


class DurationSecondsValidator(BaseModelValidator):
    """Проверка: время выполнения должно быть не более 120 секунд"""
    error_message = 'Время выполнения должно быть не более 120 секунд.'
    max_duration = 120
    
    def validate(self, habit):
        return habit.duration_seconds <= self.max_duration


class PeriodDaysValidator(BaseModelValidator):
    """Проверка: периодичность должна быть от 1 до 7 дней"""
    error_message = 'Периодичность должна быть от 1 до 7 дней.'
    min_period = 1
    max_period = 7
    
    def validate(self, habit):
        return self.min_period <= habit.period_days <= self.max_period


class PleasantHabitValidator(BaseModelValidator):
    """Проверка: приятная привычка не может иметь вознаграждения или связанной привычки"""
    error_message = 'Приятная привычка не может иметь вознаграждения или связанной привычки.'
    
    def validate(self, habit):
        if not habit.is_pleasant:
            return True
        reward_provided = habit.reward and habit.reward.strip()
        return not (reward_provided or habit.related_habit)


class RelatedHabitIsPleasantValidator(BaseModelValidator):
    """Проверка: связанная привычка должна быть приятной"""
    error_message = 'Связанная привычка должна быть приятной.'
    
    def validate(self, habit):
        if not habit.related_habit:
            return True
        return habit.related_habit.is_pleasant


class RelatedHabitNotSelfValidator(BaseModelValidator):
    """Проверка: привычка не может быть связана сама с собой"""
    error_message = 'Привычка не может быть связана сама с собой.'
    
    def validate(self, habit):
        if not habit.related_habit:
            return True
        return habit.related_habit_id != habit.pk


class HabitModelValidator:
    """Основной класс валидации модели, объединяющий все валидаторы"""
    
    def __init__(self):
        self.validators = [
            DurationSecondsValidator(),
            PeriodDaysValidator(),
            RewardAndRelatedHabitValidator(),
            PleasantHabitValidator(),
            RelatedHabitIsPleasantValidator(),
            RelatedHabitNotSelfValidator(),
        ]
    
    def __call__(self, habit):
        """Выполняет все валидаторы"""
        for validator in self.validators:
            validator(habit)


validate_habit = HabitModelValidator()

