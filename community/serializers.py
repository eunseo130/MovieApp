from rest_framework import serializers
from community.models import Article
from community.models import Comment, Article
from movies.models import Movie

# Create your views here.
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.nickname')
    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'updated_at', 'author')
        read_only_fields = ('author',)


class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.nickname')
    class Meta:
        model = Comment
        fields = ('id', 'content', 'author')


class ArticleListSerializer(serializers.ModelSerializer):
    class CommentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ('id', 'content',)
    comment_set = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Article
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    class CommentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ('id', 'content',)


    comment_set = CommentSerializer(many=True, read_only=True)
    author = serializers.ReadOnlyField(source='author.nickname')

    class Meta:
        model = Article
        fields = ('title', 'content', 'comment_set', 'author', 'movie_title', 'created_at', 'updated_at', 'id',)
        read_only_fields = ('author', 'like_users',)


