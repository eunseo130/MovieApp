from django.shortcuts import render
from rest_framework import serializers
from community.models import Article
from .models import Movie, Article

# Create your views here.
class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('pk', 'title')


class ArticleSerializer(serializers.ModelSerializer):
    class MovieSerializer(serializers.ModelSerializer):
        class Meta:
            model = Movie
            fields = ('pk', 'title')
    
    movie_set = MovieSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ('pk', 'title', 'content', 'movie_set',)