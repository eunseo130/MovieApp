# Generated by Django 3.2.3 on 2021-11-20 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0016_movie_keywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='actor',
            name='actor_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='crew',
            name='crew_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
