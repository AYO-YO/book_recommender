# user/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class UserModel(AbstractUser):

    class Meta:
        db_table = "user"

    follow = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followee')
