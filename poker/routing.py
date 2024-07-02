from django.urls import path
from .consumers import PokerConsumer

websocket_urlpatterns = [
    path(r"ws/poker/", PokerConsumer.as_asgi()),
    # path(r"ws/poker/<str:session_public_identifier>", PokerConsumer.as_asgi()),
]