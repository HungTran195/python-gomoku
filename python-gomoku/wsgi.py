"""
WSGI config for python-gomoku project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import socketio

from game.views import sio


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "python-gomoku.settings")

django_app = get_wsgi_application()
application = socketio.WSGIApp(sio, django_app)


"""
These lines of code is used to enable eventlet module on port 8000
and only used for local developement
"""
# import eventlet
# eventlet.wsgi.server(eventlet.listen(('', 8000)), application)
