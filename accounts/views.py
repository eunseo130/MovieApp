from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer
# Create your views here.
User = get_user_model()

@api_view(['POST'])
def signin(request):
    password = request.data.get('password')
    password_confirm = request.data.get('passwordConfirm')
    if password != password_confirm:
        error_message = {
            'error': '비밀번호가 일치하지 않습니다.'
        }
        return Response(error_message, status=status.HTTP)
    
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        user.set_password(password)
        user.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    context = {
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)