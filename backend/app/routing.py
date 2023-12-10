# # app/routing.py
# from django.urls import re_path
# from . import consumers

# websocket_urlpatterns = [
#     re_path(r'ws/pong/', consumers.PongConsumer.as_asgi()),
# ]


# routing.py

# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import path, re_path
# from . import consumers

# application = ProtocolTypeRouter({
#     "websocket": URLRouter([
#         path("ws/pong/", consumers.PongConsumer.as_asgi())
#     ])
# })

from django.urls import re_path 
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/pong/', consumers.PongConsumer.as_asgi())
]






