import os
import sys

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Настройка для Windows: используем solo pool вместо prefork
if sys.platform.startswith('win'):
    app.conf.worker_pool = 'solo'

app.autodiscover_tasks()
