# your_project/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.django.local')

# Create the Celery app instance.
app = Celery('config.django')

# Load task modules from all registered Django app configs.
app.config_from_object('config.django.local', namespace='CELERY')

# Autodiscover tasks defined in your Django apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
