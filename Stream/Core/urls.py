from django.urls import path
from Core.views import stream

urlpatterns = [
    path('stream/', stream, name='stream'),
]
