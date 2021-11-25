from django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    path('', views.movies_list, name='movies_list'),
    path('<int:movie_pk>/', views.movies_detail, name='movies_detail'),
    path('<int:movie_pk>/vote/', views.movies_vote_create, name='movies_vote_create'),
    path('load_movies/', views.load_movies, name='load_movies'),
    path('like/<int:movie_pk>/', views.movie_like, name='movie_like'),
    path('recommend/select/', views.recommend, name='recommend'),
    path('<int:movie_pk>/comment/', views.movie_comment_create, name='movie_comment_create'),
    path('<int:movie_pk>/comments/', views.movie_comment_list, name='movie_comment_list'),
    path('<int:movie_pk>/<int:comment_pk>/comment/', views.movie_comment_delete, name='movie_comment_delete'),
    path('<int:movie_pk>/reviews/', views.review_list, name='review_list'),
    path('<int:review_pk>/review/', views.review_detail, name='review_detail'),
    path('<int:review_pk>/like/', views.review_like, name='review_like'),
    path('<int:movie_pk>/get_movie_like/', views.get_movie_like, name='get_movie_like'),
    path('<int:review_pk>/get_review_like/', views.get_review_like, name='get_review_like'),
]
