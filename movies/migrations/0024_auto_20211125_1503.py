# Generated by Django 3.2.3 on 2021-11-25 06:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0023_auto_20211124_2154'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='vote_users',
        ),
        migrations.DeleteModel(
            name='Vote',
        ),
    ]