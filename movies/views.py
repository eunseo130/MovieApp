import requests
import random
import rest_framework

from django.shortcuts import get_list_or_404, get_object_or_404, HttpResponse, render
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from rest_framework.decorators import authentication_classes
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import Actor, Crew, Keyword, Movie, Genre, Moviecomment, Review
from .serializers import MovieListSerializer, MovieSerializer, CommentSerializer, CommentListSerializer, ReviewSerializer, ReviewListSerializer

# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def movies_list(request):
    movies = Movie.objects.all()
    serializer = MovieListSerializer(movies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def movies_detail(request, movie_pk):
    movie = get_object_or_404(Movie, movie_id=movie_pk)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)


@api_view(['GET'])
def load_movies(request):

    TMDB_URL = 'https://api.themoviedb.org/3/'
    TMDB_KEY = '1e1628fa2029e5e5102664565f10a845'
    TMDB_IMG = 'https://image.tmdb.org/t/p/w500'

# TMDB
    genres = requests.get(TMDB_URL + 'genre/movie/list' + f'?api_key={TMDB_KEY}' + '&language=ko-kr').json().get('genres')
    for genre in genres:
        context = {
            'genre_id': genre['id'],
            'name': genre['name']
        }
        genre, created = Genre.objects.get_or_create(**context)
    

    for i in range(10):
        movies = requests.get(TMDB_URL + 'movie/popular' + f'?api_key={TMDB_KEY}&page={i+1}' + '&language=ko-kr').json().get('results')
    
        for m in movies:
            movie = Movie()
            try:
                if Movie.objects.filter(movie_id=m['id']).exists() == False:
                    movie.movie_id = m['id']
                else:
                    continue
            except:
                continue
            try:
                movie.title = m['title']
            except:
                continue
            try:
                movie.overview = m['overview']
            except:
                continue
            try:
                if m['release_date'] == '':
                    continue
                movie.release_date = m['release_date']
            except:
                continue
            try:
                movie.poster_path = TMDB_IMG + m['poster_path']
            except:
                continue
            try:
                movie.popularity = m['popularity']
            except:
                continue
            try:
                movie.vote_average = m['vote_average']
            except:
                continue
            try:
                movie.vote_count = m['vote_count']
            except:
                continue
            try:
                movie.backdrop_path = m['backdrop_path']
            except:
                pass
            movie.save()
            
            for genre_id in m['genre_ids']:
                genre = Genre.objects.get(genre_id=genre_id)
                movie.genres.add(genre)
            movie_id = movie.movie_id
            
            keywords = requests.get(TMDB_URL + f'/movie/{movie_id}/keywords' + f'?api_key={TMDB_KEY}').json().get('keywords')
            for keyword in keywords:
                context = {
                    'keyword_id': keyword['id'],
                    'name': keyword['name']
                }
                keyword, created = Keyword.objects.get_or_create(**context)
                movie.keywords.add(keyword)

            credits = requests.get(TMDB_URL + f'/movie/{movie_id}/credits' + f'?api_key={TMDB_KEY}').json().get('cast')
            for credit in credits:
                if credit['known_for_department'] == 'Acting':
                    context = {
                        'actor_id': credit['id'],
                        'name': credit['original_name'],
                        'gender': credit['gender']
                    }
                    actor, created = Actor.objects.get_or_create(**context)
                    movie.actors.add(actor)
                elif credit['known_for_department'] == 'Directing' or credit['known_for_department'] == 'Writing':
                    context = {
                        'crew_id': credit['id'],
                        'name': credit['original_name'],
                        'gender': credit['gender'],
                        'job': credit['known_for_department']
                    }
                    crew, created = Crew.objects.get_or_create(**context)
                    movie.crews.add(crew)
                else:
                    pass
    return Response()


@api_view(['POST'])
@permission_classes([AllowAny])
def movie_comment_create(request, movie_pk):
    movie = get_object_or_404(Movie, movie_id=movie_pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(movie=movie, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def movie_comment_list(request, movie_pk):
    movie = get_object_or_404(Movie, movie_id=movie_pk)
    if Moviecomment.objects.all():
        comments = get_list_or_404(Moviecomment)
        comment_list = []
        for comment in comments:
            if comment.movie.movie_id == movie_pk:
                comment_list.append(comment)
        serializer = CommentListSerializer(comment_list, many=True) 
        return Response(serializer.data)
    else:
        pass
    return Response()


@api_view(['DELETE'])
@permission_classes([AllowAny])
def movie_comment_delete(request, movie_pk, comment_pk):
    comment = get_object_or_404(Moviecomment, pk=comment_pk)
    if request.user == comment.author:
        comment.delete()
        data = {
            'delete': f'?????? {comment_pk}?????? ?????????????????????.'
        }
    return Response(data, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def movie_like(request, movie_pk):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie, movie_id=movie_pk)
        user = request.user
        if movie.like_users.filter(pk=user.pk).exists():
            movie.like_users.remove(user)
            movie_liked = False
        else:
            movie.like_users.add(user)
            movie_liked = True
        movie_like_count = movie.like_users.count()
        context = {
            'movie_liked': movie_liked,
            'movie_like_count': movie_like_count,
        }
        return JsonResponse(context)
    return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def review_list(request, movie_pk):
    movie = get_object_or_404(Movie, movie_id=movie_pk)
    if request.method == 'GET':
        if Review.objects.all():
            reviews = get_list_or_404(Review)
            review_list = []
            for review in reviews:
                if review.movie.movie_id == movie_pk:
                    review_list.append(review)
            serializer = ReviewListSerializer(review_list, many=True) 
            return Response(serializer.data)
        else:
            pass
        return Response()
    
    elif request.method == 'POST':
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user, movie=movie)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE', 'PUT'])
@permission_classes([AllowAny])
def review_detail(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == 'DELETE':
        if request.user == review.author:
            review.delete()
            data = {
                'delete': f'????????? {review_pk}?????? ?????????????????????.'
            }
        return Response(data, status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'PUT':
        if request.user == review.author:
            serializer = ReviewSerializer(review, data=request.data)
            if serializer.is_valid():
                serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def recommend(request):
    if request.user.is_authenticated:
        # movies = Movie.objects.all()
        genres = Genre.objects.all()
        movie_list = []
        genre_list = []
        select = request.data
        for s in select:
            if s == '??????':
                for genre in genres:
                    if genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '???????????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == 'SF':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
            if s == '??????':
                for genre in genres:
                    if genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
            if s == '??????':
                for genre in genres:
                    if genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
            if s == '??????':
                for genre in genres:
                    if genre.name == '??????':
                        if genre.name not in genre_list:
                                genre_list.append(genre.name)
                                movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '???????????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
            if s == '??????':
                for genre in genres:
                    if genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '????????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == 'TV??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass 
            if s == '??????':
                for genre in genres:
                    if genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '???????????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '???????????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass 
            if s == '??????':
                for genre in genres:
                    if genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '????????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
            if s == '???':
                for genre in genres:
                    if genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
            if s == '???????????????':
                for genre in genres:
                    if genre.name == 'SF':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == 'TV??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
            if s == '??????':
                for genre in genres:
                    if genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == 'SF':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass 
            if s == '??????':
                for genre in genres:
                    if genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass 
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
            if s == '?????????':
                for genre in genres:
                    if genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '?????????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == '??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass
                    elif genre.name == 'TV??????':
                        if genre.name not in genre_list:
                            genre_list.append(genre.name)
                            movie_list = movie_list + list(genre.movies.all())
                        else:
                            pass

        recommended_movies = random.sample(movie_list, 10)
        serial = MovieListSerializer(recommended_movies, many=True)
    return Response(serial.data)


@api_view(['POST'])
def review_like(request, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        user = request.user
        if review.like_users.filter(pk=user.pk).exists():
            review.like_users.remove(user)
            liked = False
        else:
            review.like_users.add(user)
            liked = True
        like_count = review.like_users.count()
        context = {
            'liked': liked,
            'like_count': like_count,
        }
        return JsonResponse(context)
    return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_review_like(request, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        if request.user in review.like_users.all():
            liked = True
        else:
            liked = False
        like_count = review.like_users.count()
        context = {
                'liked': liked,
                'like_count': like_count,
            }
        return JsonResponse(context)
    return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def get_movie_like(request, movie_pk):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie, movie_id=movie_pk)
        if request.user in movie.like_users.all():
            movie_liked = True
        else:
            movie_liked = False
        movie_like_count = movie.like_users.count()
        context = {
                'movie_liked': movie_liked,
                'movie_like_count': movie_like_count,
            }
        return JsonResponse(context)
    return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)