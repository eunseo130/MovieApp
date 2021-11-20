import urllib.request
import urllib.parse
import ssl
import requests
from bs4 import BeautifulSoup

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoProject.settings")
import django
django.setup()
from movies.models import Movie, Genre


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

for i in range(25):
    movies = requests.get(TMDB_URL + 'movie/popular' + f'?api_key={TMDB_KEY}&page={i+1}' + '&language=ko-kr').json().get('results')

    for m in movies:
        movie = Movie()
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
            movie.poster_path = m['poster_path']
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
        movie.save()
        # context = {
        #     'title': movie['title'],
        #     'overview': movie['overview'],
        #     'poster_path': TMDB_IMG + movie['poster_path'],
        #     # 'release_date': movie['release_date'],
        #     'popularity': movie['popularity'],
        #     'vote_average': movie['vote_average'],
        #     'vote_count': movie['vote_count'],
        # }
        # if context['release_date'] == '':
        #     context['release_date'] = '1111-11-11'
        # movie_complete, created = Movie.objects.get_or_create(**context)
        # genre_dict = Genre.objects.all()
        # print(genre_dict)
        # try:
        #     movie_complete.release_date = movie['release_date']
        # except:
        #     continue
        for genre_id in m['genre_ids']:
            genre = Genre.objects.get(genre_id=genre_id)
            movie.genres.add(genre)
        print(movie)