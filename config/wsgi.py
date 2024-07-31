"""
WSGI config for hdbdata project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# from dotenv import dotenv_values
# config = dotenv_values(".env")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.django.production')

application = get_wsgi_application()
