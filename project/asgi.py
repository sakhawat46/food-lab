import os
import django

# Set settings module first
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

# Setup Django BEFORE importing anything from your app
django.setup()

# Now import other stuff
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.chatting.middleware import JWTAuthMiddleware
from django.core.asgi import get_asgi_application
from apps.chatting.routing import websocket_urlpatterns


# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(websocket_urlpatterns)
#     ),
# })


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})