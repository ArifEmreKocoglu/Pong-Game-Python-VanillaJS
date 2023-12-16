import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack


# Projenizin yapısına göre uygun routing modülünü içe aktarın.
# Örneğin, eğer `routing.py` dosyanız `backend` adlı bir alt klasördeyse:
import app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')


application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Django'nun standart HTTP işlemleri için
    "websocket": AuthMiddlewareStack(  # WebSocket bağlantıları için
        URLRouter(
            app.routing.websocket_urlpatterns
        )
    ),
})

