# user/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class UserModel(AbstractUser):
    class Meta:
        db_table = "user"
        verbose_name = '用户'
        verbose_name_plural = '用户'

    follow = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followee', verbose_name='关注')

    @property
    def like_books(self):
        return [like.book for like in self.likes.all()]
