from django.db import models
from django.conf import settings


# Create your models here.
class BookData(models.Model):
    class Meta:
        verbose_name = '图书'
        verbose_name_plural = '图书'
        db_table = "book_data"

    isbn = models.IntegerField('ISBN', unique=True, db_index=True)
    title = models.CharField('书籍名称', max_length=100)
    author = models.CharField('书籍作者', max_length=100)
    publisher = models.CharField('出版社', max_length=100, default='无')
    price = models.CharField('书籍标价', max_length=100, default='无')
    img_url = models.CharField('书籍图片', max_length=100, default='https://via.placeholder.com/150')
    pub_date_2 = models.DateField('发行时间', blank=True, default='', null=True)
    description = models.TextField('书籍详情', default='无')

    @property
    def proxy_img_url(self):
        return f'/proxy/image?url={self.img_url}'

    def __str__(self):
        return f"{self.id}《{self.title}》-{self.author}"

    @property
    def like_me_users(self):
        return [like.user for like in self.likes.all()]


class Like(models.Model):
    class Meta:
        db_table = "like"
        verbose_name = "喜欢的图书"
        verbose_name_plural = '喜欢的图书'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes',
                             verbose_name='用户')
    book = models.ForeignKey(BookData, on_delete=models.CASCADE, related_name='likes', verbose_name='图书')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)


class Review(models.Model):
    class Meta:
        verbose_name = '书籍评论'
        verbose_name_plural = '书籍评论'
        db_table = "review"

    content = models.TextField('评论内容')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    book = models.ForeignKey(BookData, on_delete=models.CASCADE, related_name='reviews', verbose_name='图书')
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews',
                               verbose_name='评论者')
