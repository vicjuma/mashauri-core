from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fiberIS.settings')

app = Celery('fiberIS')
app.conf.enable_utc = False

app.config_from_object(settings, namespace='CELERY')

app.conf.beat_schedule = {
    # 9 AM Task
    'send-mail-every-9am': {
        'task': 'mashauri.tasks.nine_am',  # The task name from tasks.py
        'schedule': crontab(hour=9, minute=0),  # Schedule for 9 AM
    },
    # 12 Noon Task
    'send-mail-every-noon': {
        'task': 'mashauri.tasks.twelve_noon',  # The task name from tasks.py
        'schedule': crontab(hour=12, minute=0),  # Schedule for 12 PM
    },
    # 4 PM Task
    'send-mail-every-4pm': {
        'task': 'mashauri.tasks.four_pm',  # The task name from tasks.py
        'schedule': crontab(hour=16, minute=0),  # Schedule for 4 PM
    },
    # Update expired dispatches
    'update-expired-dispatches': {
        'task': 'mashauri.tasks.update_expired_dispatches',
        'schedule': crontab(minute='*/5'),  # Schedule for 4 PM
    },
     # SLA Escalation Matrix
    'send-sla-matrix-emails': {
        'task': 'mashauri.tasks.send_sla_matrix_emails',
        'schedule': crontab(minute=0),
    },
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
