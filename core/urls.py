from django.urls import path
from .views import send_data

urlpatterns = [
    path('calculate/', send_data)
]
