from django.contrib import admin
from .models import Movie, Actor, Crew, Genre, Vote


# Register your models here.
admin.site.register(Movie)
admin.site.register(Actor)
admin.site.register(Crew)
admin.site.register(Genre)
admin.site.register(Vote)