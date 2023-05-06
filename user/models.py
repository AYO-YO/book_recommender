# user/models.py
import functools

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from common import algorithm


class UserModel(AbstractUser):
    class Meta:
        db_table = "user"
        verbose_name = '用户'
        verbose_name_plural = '用户'

    follow = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followee', verbose_name='关注')

    @property
    def like_books(self):
        return [like.book for like in self.likes.all()]

    @classmethod
    def get_co_matrix(cls):
        """获取所有用户的所有评分数据，用于构造共观矩阵，示例：
        {
            '用户A': {'唐伯虎点秋香': 5, '逃学威龙1': 1, '追龙': 2},
            '用户B': {'唐伯虎点秋香': 4, '喜欢你': 2, '暗战': 3.5},
            '用户C': {'逃学威龙1': 2, '他人笑我太疯癫': 4},
            '用户D': {'喜欢你': 4, '暗战': 3},
            '用户E': {'逃学威龙1': 4, '他人笑我太疯癫': 3}
        }
        """
        return {
            user.username: {
                review.book.title: review.score
                for review in user.reviews.all()
            }
            for user in cls.objects.all() if user.reviews.count()
        }

    def recommend_books(self):
        """给当前用户推荐图书"""

        data = UserModel.get_co_matrix()

        # 计算物品相似矩阵
        W = algorithm.similarity(data)
        return algorithm.recommend_list(data, W, self.username)
