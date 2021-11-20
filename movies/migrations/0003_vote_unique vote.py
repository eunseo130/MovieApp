# Generated by Django 3.2.3 on 2021-11-18 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_auto_20211118_0952'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='vote',
            constraint=models.UniqueConstraint(fields=('user', 'movie'), name='unique vote'),
        ),
    ]