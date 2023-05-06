# user/views.py
# user/views.py
from django.contrib import auth  # 用户自上而下功能
# user/views.py
from django.contrib.auth import get_user_model  # 检查用户是否存在的函数
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Avg

from book.models import Like, Review, BookData
from .models import UserModel


def sign_up_view(request):
    first_like = BookData.objects.annotate(avg_score=Avg("reviews__score")).order_by("-avg_score")[:50]

    if request.method == 'GET':
        user = request.user.is_authenticated  # 检查登录用户是否请求
        if user:  # 如果您已登录
            return redirect('/')
        else:  # 如果您没有登录

            return render(request, 'signup.html', {'bestseller':first_like})

    elif request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        my_book = request.POST.get('book', '')
        if password != password2:
            # 需要错误，因为密码不同。{“error”：创建并传递“错误语句”}
            return render(request, 'signup.html', {'bestseller':first_like, 'error': '请检查密码！!'})
        else:
            if username == '' or password == '':
                # 用户名和密码对于用户存储是必需的。
                return render(request, 'signup.html', {'bestseller':first_like, 'error': '用户名和密码是必需的'})


            exist_user = get_user_model().objects.filter(username=username)
            if exist_user:
                return render(request, 'signup.html',
                              {'error': '用户存在'})  # 重新浮出会员页面，而不保存用户，因为用户存在
            else:
                UserModel.objects.create_user(username=username, password=password)

                first_book=Like()
                like_users_id=UserModel.objects.values().order_by('-id')
                like_book_id=BookData.objects.filter(isbn=int(my_book)).values()
                first_book.user_id=like_users_id[0]['id']
                first_book.book_id= list(like_book_id)[0]['id']

                first_book.save()

                return redirect('/sign-in')  # 注册完成后，转到登录页面



# user/views.py

def sign_in_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', "")
        password = request.POST.get('password', "")

        me = auth.authenticate(request, username=username, password=password)  #载入用户
        if me is not None:  # 将保存用户的密码与输入的密码进行比较
            auth.login(request, me)
            return redirect('/')
        else:

            return render(request,'signin.html',{'error':'请检查您的用户名或密码'})  # 登录失败


    elif request.method == 'GET':
        user = request.user.is_authenticated
        if user:
            return redirect('/')
        else:
            return render(request, 'signin.html')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required
def user_follow(request, id):
    me = request.user
    click_user = UserModel.objects.get(id=id)
    if me in click_user.followee.all():
        click_user.followee.remove(request.user)
    else:
        click_user.followee.add(request.user)
    return redirect('/user/')


def user_view(request):
    if request.method == 'GET':
        # 载入用户，使用 exclude 和 request.user.username 排除“已登录的用户”
        user_list = UserModel.objects.all().exclude(username=request.user.username)
        return render(request, 'user_list.html', {'user_list': user_list})


# 简介

# def profile_view(request, id):
#     if id is None:
#         me = request.user
#         books = BookModel.objects.filter(user_id=me.id)
#         reviews = ReviewModel.objects.filter(author=me.id)
#
#     else:
#         books = BookModel.objects.filter(user_id=id)
#         reviews = ReviewModel.objects.filter(author=id)
#
#     return render(request, 'profile.html', {'books':books, 'reviews':reviews})


def profile_view(request, id):
    user = request.user.is_authenticated
    if user:
        profile_book = Like.objects.filter(user_id=id)
        profile_review = Review.objects.filter(writer_id=id)
        profile_user = UserModel.objects.filter(id=id)

        return render(request, 'profile.html', {'profile_book': profile_book,
                                                'profile_review': profile_review,
                                                'profile_user': profile_user,
                                                })
    else:
        return redirect('/sign-in')



