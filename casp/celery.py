from __future__ import absolute_import

import os

from celery import Celery

import configurations

from django.conf import settings

import dotenv

try:
    dotenv.read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
except:
    pass

ENVIRONMENT = os.getenv('ENVIRONMENT', 'DEVELOPMENT').title()

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'casp.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', ENVIRONMENT)
configurations.setup()

app = Celery('casp')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))