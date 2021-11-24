# Generated by Django 3.2.3 on 2021-11-23 07:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0021_moviecomment_review'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='vote',
            name='unique vote',
        ),
        migrations.AlterField(
            model_name='vote',
            name='score',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]