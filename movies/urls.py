from django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    path('', views.movies_list_create, name='movies_list_create'),
    path('<int:movie_pk>/', views.movies_detail_update_delete, name='movies_detail_update_delete'),
    path('<int:movie_pk>/vote/', views.movies_vote_create, name='movies_vote_create'),
    path('<int:movie_pk>/vote/<int:vote_pk>', views.movies_vote_update_delete, name='movies_vote_update_delete'),
    path('get_movies/', views.get_movies, name='get_movies')
]
