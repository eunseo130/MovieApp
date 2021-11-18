from django.shortcuts import get_object_or_404, render

from rest_framework import status
import rest_framework
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from rest_framework.decorators import authentication_classes
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import Movie, Vote
from .serializers import MovieListSerializer, MovieSerializer, VoteSerializer

# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def movies_list_create(request):
    if request.method == 'GET':
        movies = Movie.objects.all()
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = MovieSerializer(request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def movies_detail_update_delete(request, movie_pk):

    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'GET': 
        serializer = MovieSerializer(movie)
        return Response(serializer.data)
    else:
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        if request.method == 'PUT':
            serializer = MovieSerializer(movie, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        elif request.method == 'DELETE':
            movie.delete()
            return Response({ 'id': movie_pk }, status=status.HTTP_204_NO_CONTENT)



@api_view(['POST'])
def movies_vote_create(request, movie_pk):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    movie = get_object_or_404(Movie, pk=movie_pk)
    serializer = VoteSerializer(request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(commit=False)
        serializer.user = request.user
        serializer.movie = movie
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(['PUT', 'DELETE'])
def movies_vote_update_delete(request, movie_pk, vote_pk):    
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)    
    
    movie = get_object_or_404(Movie, pk=movie_pk)
    vote = get_object_or_404(Vote, pk=vote_pk)
    if request.method == 'PUT':
        serializer = VoteSerializer(vote, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)        
    elif request.method == 'DELETE':
        vote.delete()
        return Response({ 'movie_id': movie_pk, 'vote_pk': vote_pk }, status=status.HTTP_204_NO_CONTENT)