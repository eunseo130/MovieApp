# Generated by Django 3.2.3 on 2021-11-22 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0019_movie_backdrop_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='backdrop_path',
            field=models.TextField(blank=True, null=True),
        ),
    ]
