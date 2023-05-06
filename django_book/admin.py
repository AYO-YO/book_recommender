from django.contrib.admin import AdminSite
from user.models import UserModel
from book.models import BookData, Like, Review
from django.contrib.auth.models import Permission


class CustomAdminSite(AdminSite):
    site_header = '图书管理后台'
    site_title = '图书管理后台'


book_admin = CustomAdminSite(name='图书管理')
book_admin.register(UserModel)
book_admin.register(BookData)
book_admin.register(Like)
book_admin.register(Review)
book_admin.register(Permission)
