from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from . import views

urlpatterns = [
    path('signin/', views.signin),
    path('profile/', views.profile),
    path('api-token-auth/', obtain_jwt_token),
]