from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'funpay_bot.settings')

app = Celery("funpay_bot")

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True, track_started=True)
def update_items():
    pass
