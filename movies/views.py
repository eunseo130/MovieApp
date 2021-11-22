import requests
import random
from django.shortcuts import get_list_or_404, get_object_or_404, HttpResponse, render
from django.http.response import JsonResponse

from rest_framework import status
import rest_framework
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from rest_framework.decorators import authentication_classes
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import Actor, Crew, Keyword, Movie, Vote, Genre
from .serializers import MovieListSerializer, MovieSerializer, VoteSerializer

# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def movies_list_create(request):
    movies = Movie.objects.all()
    serializer = MovieListSerializer(movies, many=True)
    return Response(serializer.data)


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
def load_movies(request):
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
def movie_like(request, movie_pk):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie, pk=movie_pk)
        user = request.user
        if movie.like_users.filter(pk=user.pk).exists():
            movie.like_users.remove(user)
            liked = False
        else:
            movie.like_users.add(user)
            liked = True
        like_count = movie.like_users.count()
        context = {
            'liked': liked,
            'like_count': like_count,
        }
        return JsonResponse(context)
    return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def recommend(request, select):
    if request.user.is_authenticated:
        movies = Movie.objects.all()
        genres = Genre.objects.all()
        movie_list = []
        if select == '양식':
            for genre in genres:
                if genre.name == '액션':
                    movie_list.append(genre.movies.all())
                elif genre.name == '모험':
                    movie_list.append(genre.movies.all())
                elif genre.name == '애니메이션':
                    movie_list.append(genre.movies.all())
                elif genre.name == '판타지':
                    movie_list.append(genre.movies.all())
                elif genre.name == 'SF':
                    movie_list.append(genre.movies.all())
                elif genre.name == '서부':
                    movie_list.append(genre.movies.all())
                elif genre.name == '로맨스':
                    movie_list.append(genre.movies.all())
                elif genre.name == '음악':
                    movie_list.append(genre.movies.all())
        if select == '중식':
            for genre in genres:
                if genre.name == '액션':
                    movie_list.append(genre.movies.all())
                elif genre.name == '모험':
                    movie_list.append(genre.movies.all())
                elif genre.name == '애니메이션':
                    movie_list.append(genre.movies.all())
        # if select == '양식':
        #     for movie in movies:
        #         if ('액션',) in movie.genres.values_list('name'):
        #             if movie not in movie_list:
        #                 movie_list.append(movie)
        #         elif ('모험',) in movie.genres.values_list('name'):
        #             if movie not in movie_list:
        #                 movie_list.append(movie)
        #         elif ('애니메이션',) in movie.genres.values_list('name'):
        #             if movie not in movie_list:
        #                 movie_list.append(movie)
        #         elif ('판타지',) in movie.genres.values_list('name'):
        #             if movie not in movie_list:
        #                 movie_list.append(movie)
        #         elif ('SF',) in movie.genres.values_list('name'):
        #             if movie not in movie_list:
        #                 movie_list.append(movie)
        #         elif ('서부',) in movie.genres.values_list('name'):
        #             if movie not in movie_list:
        #                 movie_list.append(movie)
        #         elif ('로맨스',) in movie.genres.values_list('name'):
        #             if movie not in movie_list:
        #                 movie_list.append(movie)
        #         elif ('음악',) in movie.genres.values_list('name'):
        #             if movie not in movie_list:
        #                 movie_list.append(movie)
        elif select == '중식':
            for movie in movies:
                if ('역사',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('드라마',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('범죄',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
        elif select == '한식':
            for movie in movies:
                if ('가족',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('드라마',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('코미디',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('로맨스',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('음악',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)        
        elif select == '일식':
            for movie in movies:
                if ('가족',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('드라마',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('판타지',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('애니메이션',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('공포',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)     
        elif select == '분식':
            for movie in movies:
                if ('가족',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('미스터리',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('TV영화',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
        elif select == '간식':
            for movie in movies:
                if ('스릴러',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('다큐멘터리',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('코미디',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('애니메이션',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
        elif select == '면류':
            for movie in movies:
                if ('모험',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('미스터리',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('음악',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
        elif select == '빵':
            for movie in movies:
                if ('서부',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('액션',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('드라마',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('로맨스',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
        elif select == '패스트푸드':
            for movie in movies:
                if ('SF',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('TV영화',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('스릴러',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
        elif select == '혼술':
            for movie in movies:
                if ('전쟁',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('범죄',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('액션',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('모험',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('판타지',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('SF',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('스릴러',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
        elif select == '매운':
            for movie in movies:
                if ('액션',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('범죄',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('판타지',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('공포',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('스릴러',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('전쟁',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
        elif select == '느끼한':
            for movie in movies:
                if ('음악',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('로맨스',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('드라마',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('가족',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                elif ('TV영화',) in movie.genres.values_list('name'):
                    if movie not in movie_list:
                        movie_list.append(movie)
                    # movie_list.append(genre.movies.filter(genre=))
                # or 12 in movies.genres or 16 in movies.genres or 14 in movies.genres or 878 in movies.genres or 37 in movies.genres or 10749 in movies.genres or 10402 in movies.genres:
                    # movie_list.append(movie)
        # recommended_movies = random.sample(movie_list, 3)
        # print(recommended_movies)
        print(movie_list)
                # for genre in genres:
                    
            #     recommend_movie = Movie.objects.filter(genre)
    return HttpResponse(movie_list)