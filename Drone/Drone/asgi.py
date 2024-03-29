"""
ASGI config for Drone project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Drone.settings')

application = get_asgi_application()

from django.urls import path
from Core.consumers import DroneConsumer  # Import the DroneConsumer class

ws_patterns = [
    path('drone/', DroneConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    # "http": get_asgi_application(),
    "websocket": URLRouter(ws_patterns),
})
