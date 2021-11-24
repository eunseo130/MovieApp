from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.contrib.auth.decorators import login_required

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from community.serializers import ArticleSerializer, CommentSerializer, ArticleListSerializer, CommentListSerializer
from .models import Article, Comment

# Create your views here.\
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def article_list(request):
    if request.method == 'GET':
        articles = get_list_or_404(Article)
        serializer = ArticleListSerializer(articles, many=True) 
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes([AllowAny])
def article_detail(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    if request.method == 'GET':
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        if request.user == article.author:
            article.delete()
            data = {
                'delete': f'게시글 {article_pk}번이 삭제되었습니다.'
            }
        return Response(data, status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PUT':
        if request.user == article.author:
            serializer = ArticleSerializer(article, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def comment_list(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    comments = get_list_or_404(Comment)
    comment_list = []
    for comment in comments:
        if comment.article.pk == article_pk:
            comment_list.append(comment)
    serializer = CommentListSerializer(comment_list, many=True) 
    return Response(serializer.data)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def comment_create(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(article=article, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def comment_delete(request, article_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user == comment.author:
        comment.delete()
        data = {
            'delete': f'댓글 {comment_pk}번이 삭제되었습니다.'
        }
    return Response(data, status=status.HTTP_204_NO_CONTENT)



@api_view(['POST'])
@login_required
def like(request, article_pk):
    if request.user.is_authenticated:
        article = get_object_or_404(Article, pk=article_pk)
        user = request.user
        if article.like_users.filter(pk=user.pk).exists():
            article.like_users.remove(user)
            liked = False
        else:
            article.like_users.add(user)
            liked = True
        like_count = article.like_users.count()
        context = {
            'liked': liked,
            'like_count': like_count,
        }
        return JsonResponse(context)
    return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)