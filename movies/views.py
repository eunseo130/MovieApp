import requests
import json
from django.shortcuts import get_list_or_404, get_object_or_404, HttpResponse, render

from rest_framework import status
import rest_framework
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from rest_framework.decorators import authentication_classes
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import Movie, Vote, Genre
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
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
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


@api_view(['GET'])
def get_movies(request):
    # KOBIS_URL = 'http://www.kobis.or.kr/kobisopenapi/webservice/rest/'
    # KOBIS_KEY = '25d9f0ae55ce925524fd90e423bcf7ca'

    TMDB_URL = 'https://api.themoviedb.org/3/'
    TMDB_KEY = '1e1628fa2029e5e5102664565f10a845'
    TMDB_IMG = 'https://image.tmdb.org/t/p/w500'


# 영화진흥위원회

# res = requests.get(
#     'https://kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json?key=25d9f0ae55ce925524fd90e423bcf7ca&openStartDt=1996').json()

# print(res)
# res = res.get("movieListResult").get("movieList")
# print(len(res))

# TMDB
    movie_info = []
    genres = requests.get(TMDB_URL + 'genre/movie/list' + f'?api_key={TMDB_KEY}' + '&language=ko-kr').json().get('genres')
    for genre in genres:
        context = {
            'genre_id': genre['id'],
            'name': genre['name']
        }
        genre, created = Genre.objects.get_or_create(**context)
    
    for i in range(10):
        movies = requests.get(TMDB_URL + 'movie/popular' + f'?api_key={TMDB_KEY}&page={i+1}' + '&language=ko-kr').json().get('results')
    
        for movie in movies:
            context = {
                'title': movie['title'],
                'overview': movie['overview'],
                'poster_path': TMDB_IMG + movie['poster_path'],
                'release_date': movie['release_date'],
                'popularity': movie['popularity'],
                'vote_average': movie['vote_average'],
                'vote_count': movie['vote_count'],
                # 'runtime': movie['runtime'],
                # 'revenue': movie['revenue'],\
            }
            movie_complete, created = Movie.objects.get_or_create(**context)
            # genre_dict = Genre.objects.all()
            # print(genre_dict)
            for genre_id in movie['genre_ids']:
                genre = Genre.objects.get(genre_id=genre_id)
                movie_complete.genres.add(genre)
    return Response()