from django.urls import path
from .views import ChatAPIView, InitialMessageAPIView, ClosingMessageAPIView

urlpatterns = [
    path('chatbot/', ChatAPIView.as_view(), name='chatbot_api'),
    path('chatbot/initial/', InitialMessageAPIView.as_view(), name='initial_message'),
    path('chatbot/closing/', ClosingMessageAPIView.as_view(), name='closing_message'),
]
