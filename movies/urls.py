from django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    path('', views.movies_list, name='movies_list'),
    path('<int:movie_pk>/', views.movies_detail, name='movies_detail'),
    path('<int:movie_pk>/vote/', views.movies_vote_create, name='movies_vote_create'),
    path('<int:movie_pk>/vote/<int:vote_pk>', views.movies_vote_update_delete, name='movies_vote_update_delete'),
    path('load_movies/', views.load_movies, name='load_movies'),
    path('like/<int:movie_pk>/', views.movie_like, name='movie_like'),
    path('recommend/select/', views.recommend, name='recommend'),
    path('<int:movie_pk>/comment/', views.movie_comment_create, name='movie_comment_create'),
    path('<int:movie_pk>/comments/', views.movie_comment_list, name='movie_comment_list'),
    path('<int:movie_pk>/reviews/', views.review_list, name='review_list')
]
