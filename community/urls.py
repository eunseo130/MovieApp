from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.article_list),
    path('articles/<int:article_pk>/', views.article_detail),
    path('comments/<int:article_pk>/', views.comment_list),
    path('comment_create/<int:article_pk>/', views.comment_create),
    path('comment/<int:article_pk>/<int:comment_pk>/', views.comment_detail),
    path('like/<int:article_pk>/', views.like)
]
