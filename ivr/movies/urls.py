from django.urls import path

from . import views

urlpatterns = [
    path('answer', views.choose_theater, name='choose-theater'),
    path('choose-movie', views.choose_movie, name='choose-movie'),
    path('list-shows', views.list_shows, name='list-shows'),
]
