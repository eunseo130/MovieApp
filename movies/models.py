from django.db import models
from django.conf import settings

class Actor(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)

class Crew(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    job = models.CharField(max_length=50)

class Genre(models.Model):
    name = models.CharField(max_length=50)

class Movie(models.Model):
    actors = models.ManyToManyField(Actor)
    crews = models.ManyToManyField(Crew)
    name = models.CharField(max_length=100)
    overview = models.TextField()
    poster_path = models.TextField()
    release_date = models.DateField()
    popularity = models.FloatField()
    vote_average = models.FloatField()
    vote_count = models.IntegerField()
    runtime = models.IntegerField()
    revenue = models.IntegerField()
    genres = models.ManyToManyField(Genre)
    like = models.ManyToManyField(settings.AUTH_USER_MODEL) 
