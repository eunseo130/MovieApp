from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.fields import related

class Actor(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    actor_id = models.IntegerField()

    def __str__(self):
        return self.name

class Crew(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    job = models.CharField(max_length=50)
    crew_id = models.IntegerField()

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=50)
    genre_id = models.IntegerField()

    def __str__(self):
        return self.name


class Keyword(models.Model):
    keyword_id = models.IntegerField()
    name = models.TextField()

    def __str__(self):
        return self.name


class Movie(models.Model):
    movie_id = models.IntegerField()
    title = models.CharField(max_length=100)
    overview = models.TextField()
    poster_path = models.TextField()
    release_date = models.DateField(blank=True, null=True, default=1111-11-11)
    popularity = models.FloatField()
    vote_average = models.FloatField()
    vote_count = models.IntegerField()
    backdrop_path = models.TextField(null=True, blank=True)
    actors = models.ManyToManyField(Actor, related_name="movies")
    crews = models.ManyToManyField(Crew, related_name="movies")
    genres = models.ManyToManyField(Genre, related_name="movies")
    keywords = models.ManyToManyField(Keyword, related_name="movies")
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="movie_like")
    vote_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="vote_movies", through='Vote', through_fields=('movie', 'user'))

    def __str__(self):
        return self.title

class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['user', 'movie'],
                name='unique vote',
            ),
        ]
    
    def __str__(self):
        return f'{self.user} vote to {self.movie}'


class Moviecomment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="movie")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="movie_comment_author")


class Review(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="review_movie")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_author")
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="review_like")