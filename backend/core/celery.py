from __future__ import absolute_import, unicode_literals
from datetime import datetime
import os

import pytz
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'update-installment-statuses': {
        'task': 'plans.tasks.update_installment_statuses',
        'schedule': crontab(minute=5, hour=0, nowfun=lambda: datetime.now(pytz.timezone('Asia/Riyadh'))),
    },
    'check-upcoming-installments': {
        'task': 'plans.tasks.check_upcoming_installments_task',
        'schedule': crontab(minute=0, hour=9, nowfun=lambda: datetime.now(pytz.timezone('Asia/Riyadh'))),  # Run at 9 AM every day
    },
}