from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, UserManager, PermissionsMixin


class User(AbstractUser):
    nickname = models.CharField(verbose_name='nickname', max_length=20, unique=True)
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)
    USERNAME_FIELD = email
    

    
