"""
WSGI config for caro_game project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import socketio
import eventlet
from django.contrib.staticfiles.handlers import StaticFilesHandler

from game.views import sio

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_example.settings")

django_app = get_wsgi_application()
application = socketio.Middleware(
    sio, wsgi_app=django_app, socketio_path='socket.io')


eventlet.wsgi.server(eventlet.listen(('', 8000)), application)


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daily_news.settings')

# application = get_wsgi_application()
