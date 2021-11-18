from rest_framework import serializers
from movies.models import Movie, Actor, Crew, Genre, Vote
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('pk', 'title')


class MovieSerializer(serializers.ModelSerializer):

    class ActorSerializer(serializers.ModelSerializer):
        class Meta:
            model = Actor
            fields = ('pk', 'name')
    
    class CrewSerializer(serializers.ModelSerializer):
        class Meta:
            model = Crew
            fields = ('pk', 'name', 'job')
    
    class GenreSerializer(serializers.ModelSerializer):
        class Meta:
            model = Genre
            fields = ('pk', 'name')
    
    actors = ActorSerializer(many=True, read_only=True)
    crews = CrewSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        # fields = ('pk', 'title', 'overview', 'poster_path', 'release_date', 'popularity', 'vote_average', 'vote_count', 'rutime', 'revenue', 'actors', 'crews', 'genres')
        field = '__all__'
        exclude = ('like_users', 'vote_users')


class VoteSerializer(serializers.ModelSerializer):
    class MovieSerializer(serializers.ModelSerializer):
        class Meta:
            model = Movie
            fields = ('pk', 'title')

    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('pk', 'nickname')
        
    movie = MovieSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = '__all__'
