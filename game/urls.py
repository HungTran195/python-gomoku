from django.urls import path, re_path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:game_id>', views.invited_game, name='invited_game'),
    # path('', views.lobby, name='lobby'),
    # path('', views.move, name='move'),
]
