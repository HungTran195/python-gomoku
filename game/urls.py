from django.urls import path
from . import views

app_name = 'caro_game'

urlpatterns = [
    path('', views.lobby, name='lobby'),
]
