import logging
from django.utils import timezone
from celery import shared_task

from tracker.models import Habit
from tracker.services import send_tg_reminder

logger = logging.getLogger(__name__)


@shared_task
def send_reminder_notification():
    """Периодическая задача для проверки и отправки напоминаний о привычках."""
    from django.utils import timezone as tz
    from django.conf import settings
    import pytz
    
    # Получаем текущее время в локальном часовом поясе проекта
    local_tz = pytz.timezone(settings.TIME_ZONE)
    current_datetime = tz.now().astimezone(local_tz)
    current_time = current_datetime.time()
    current_date = current_datetime.date()
    
    logger.info(f"Проверка напоминаний. Текущее время (локальное): {current_time}")

    habits = Habit.objects.filter(time_of_day__isnull=False)
    logger.info(f"Найдено привычек с указанным временем: {habits.count()}")
    
    sent_count = 0
    for habit in habits:
        logger.info(f"Проверка привычки {habit.id}: время={habit.time_of_day}, владелец={habit.owner.email}, tg_chat_id={habit.owner.tg_chat_id}")

        if habit.time_of_day:
            current_minutes = current_time.hour * 60 + current_time.minute
            habit_minutes = habit.time_of_day.hour * 60 + habit.time_of_day.minute
            time_diff = abs(current_minutes - habit_minutes)
            logger.info(f"Разница во времени для привычки {habit.id}: {time_diff} минут (текущее={current_time}, привычка={habit.time_of_day})")
        
        if should_send_reminder(habit, current_time, current_date):
            logger.info(f"Время совпадает для привычки {habit.id}")
            
            if habit.owner.tg_chat_id:
                message = format_reminder_message(habit)
                logger.info(f"Отправка напоминания для привычки {habit.id} пользователю {habit.owner.email}")

                try:
                    send_tg_reminder(habit.owner.tg_chat_id, message)
                    sent_count += 1
                    logger.info(f"Напоминание успешно отправлено для привычки {habit.id}")
                except Exception as e:
                    logger.error(f"Ошибка при отправке напоминания для привычки {habit.id}: {str(e)}", exc_info=True)
            else:
                logger.warning(f"У пользователя {habit.owner.email} не указан tg_chat_id для привычки {habit.id}")
        else:
            logger.info(f"Время не совпадает для привычки {habit.id}: текущее={current_time}, привычка={habit.time_of_day}")
    
    result = {
        'status': 'success',
        'reminders_sent': sent_count,
        'checked_at': timezone.now().isoformat()
    }
    logger.info(f"Задача завершена: {result}")
    return result


def should_send_reminder(habit, current_time, current_date):
    """Определяет, нужно ли отправить напоминание для привычки."""
    if not habit.time_of_day:
        return False

    habit_time = habit.time_of_day

    current_minutes = current_time.hour * 60 + current_time.minute
    habit_minutes = habit_time.hour * 60 + habit_time.minute
    time_diff = abs(current_minutes - habit_minutes)

    if time_diff > 1:
        return False
    
    return True


def format_reminder_message(habit):
    """Форматирует сообщение напоминания о привычке."""
    time_str = habit.time_of_day.strftime('%H:%M') if habit.time_of_day else 'любое время'
    place_str = f" в {habit.place}" if habit.place else ""
    
    message = (
        f"! Напоминание о привычке!\n\n"
        f"Я буду {habit.action}{place_str} в {time_str}.\n"
        f"Время выполнения: {habit.duration_seconds} секунд."
    )
    
    if habit.reward:
        message += f"\nВознаграждение: {habit.reward}"
    elif habit.related_habit:
        message += f"\nПосле выполнения: {habit.related_habit.action}"
    
    return message

