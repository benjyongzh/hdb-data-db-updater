"""
ASGI config for hdbdata project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# from dotenv import dotenv_values
# config = dotenv_values(".env")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.django.production')

application = get_asgi_application()
