from django.utils import timezone

from celery import shared_task



@shared_task
def send_reminder_notification():
    current_date = timezone.now().date()

    
