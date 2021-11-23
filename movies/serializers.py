from rest_framework import serializers
from movies.models import Movie, Actor, Crew, Genre, Vote, Moviecomment, Review
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.nickname')
    class Meta:
        model = Moviecomment
        fields = ('id', 'content', 'created_at', 'updated_at', 'author')
        read_only_fields = ('author',)


class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.nickname')
    class Meta:
        model = Moviecomment
        fields = ('id', 'content', 'author')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.nickname')
    class Meta:
        model = Review
        fields = ('id', 'title', 'content', 'created_at', 'updated_at', 'author')
        read_only_fields = ('author',)


class ReviewListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.nickname')
    class Meta:
        model = Review
        fields = ('id', 'content', 'author', 'title',)


class MovieSerializer(serializers.ModelSerializer):

    class ActorSerializer(serializers.ModelSerializer):
        class Meta:
            model = Actor
            fields = ('pk', 'name', 'actor_id')
    
    class CrewSerializer(serializers.ModelSerializer):
        class Meta:
            model = Crew
            fields = ('pk', 'name', 'job')
    
    class GenreSerializer(serializers.ModelSerializer):
        class Meta:
            model = Genre
            fields = ('pk', 'name')
    
    class CommentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Moviecomment
            fields = ('id', 'content',)

    class ReviewSerializer(serializers.ModelSerializer):
        class Meta:
            model = Review
            fields = ('id', 'content', 'created_at', 'updated_at', 'author')
            read_only_fields = ('author',)

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

