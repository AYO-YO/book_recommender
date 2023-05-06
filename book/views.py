from datetime import datetime

import gensim.models
import jieba
import pandas as pd
import requests
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from book.models import BookData, Like, Review
from user.models import UserModel

jieba.initialize()


def loading(request):
    user = request.user.is_authenticated
    if user:
        return render(request, 'loading.html')
    else:
        return redirect('/sign-in')


@csrf_exempt
def loading_proc(request):
    if request.method == 'POST':
        response = {
            'url': 'home'
        }
        return JsonResponse(response)


def home(request):
    user = request.user.is_authenticated
    if user:
        return redirect('/book')
    else:
        return redirect('/sign-in')


def get_bestseller_list():
    bestseller_list = BookData.objects.filter(isbn__range=['1', '70'])
    # paginator = Paginator(bestseller_list, 10)
    # try:
    #     bestseller_list = paginator.page(page)
    # except PageNotAnInteger:
    #     bestseller_list = paginator.page(1)
    # except EmptyPage:
    #     bestseller_list = paginator.page(paginator.num_pages)
    return bestseller_list


def get_recommend_list(request, id):
    df = pd.DataFrame(list(BookData.objects.all().values()))
    user = request.user.is_authenticated
    if not user:
        return redirect('/sign-in')

    user_id = UserModel.objects.get(id=request.user.id)
    selected_book = BookData.objects.get(id=id)
    page = request.GET.get('page', 1)
    profile_book = Like.objects.filter(user_id=user_id)
    model = gensim.models.Doc2Vec.load('book/doc2vec/model.doc2vec')

    # 标记选定的图书
    tmp = jieba.lcut(selected_book.title)
    tmp2 = jieba.lcut(selected_book.description)
    tokens = []

    for word in tmp + tmp2:
        if word != '|':
            tokens.append(word)

    inferred_doc_vec = model.infer_vector(tokens)
    most_similar_docs = model.docvecs.most_similar([inferred_doc_vec], topn=101)
    recommend_list = []

    for index, similarity in most_similar_docs:

        # 自己被排除在推荐书之外
        if df['isbn'][index] == selected_book.isbn:
            continue

        recommend_list.append(
            {'id': df['id'][index], 'isbn': df['isbn'][index], 'title': df['title'][index],
             'img_url': df['img_url'][index],
             'description': df['description'][index], 'author': df['author'][index], 'price': df['price'][index],
             'pub_date_2': df['pub_date_2'][index],
             'publisher': df['publisher'][index],
             'proxy_img_url': BookData.objects.get(id=df['id'][index]).proxy_img_url}
        )

    paginator = Paginator(recommend_list, 20)
    try:
        recommend_list = paginator.page(page)
    except PageNotAnInteger:
        recommend_list = paginator.page(1)
    except EmptyPage:
        recommend_list = paginator.page(paginator.num_pages)

    return render(request, 'home.html',
                  {'all_book': recommend_list, 'profile_book': profile_book, 'selected_book': selected_book.title,
                   'bestseller_list': get_bestseller_list()})


def get_book(request):
    user = request.user.is_authenticated
    if not user:
        return redirect('/sign-in')

    if request.method == 'GET':
        user = UserModel.objects.get(id=request.user.id)
        book_list = BookData.objects.all()
        total_book = book_list.count()
        search_text = request.GET.get('search_text', '')
        page = request.GET.get('page', 1)
        profile_book = user.get_recommends_book_model_and_score()
        print(profile_book)

        if search_text != '':
            if len(search_text) < 2:
                messages.warning(request, "搜索词必须至少包含 2 个字符。")
                return redirect('/book')

            result_list = book_list.filter(
                Q(title__icontains=search_text) |
                Q(author__icontains=search_text) |
                Q(publisher__icontains=search_text)
            )
            total_book = result_list.count()
            # for book in book_list:
            #     if search_text in book['author'] or search_text in book['title'] or search_text in book['publisher']:
            #         result_list.append(book)

            paginator = Paginator(result_list, 20)
            try:
                result_list = paginator.page(page)
            except PageNotAnInteger:
                result_list = paginator.page(1)
            except EmptyPage:
                result_list = paginator.page(paginator.num_pages)

            return render(request, 'home.html',
                          {'all_book': result_list, 'search_text': search_text, 'profile_book': profile_book,
                           'total_book': total_book, 'bestseller_list': get_bestseller_list()})

        else:
            paginator = Paginator(book_list, 20)
            try:
                book_list = paginator.page(page)
            except PageNotAnInteger:
                book_list = paginator.page(1)
            except EmptyPage:
                book_list = paginator.page(paginator.num_pages)
            return render(request, 'home.html',
                          {'all_book': book_list, 'profile_book': profile_book, 'total_book': total_book,
                           'bestseller_list': get_bestseller_list()})


# def detail_book(request, id):
#     # book = (bookDB).objects.get(id=id)
#     book = {'title': '标题' + str(id), 'author': '作者' + str(id), 'publisher': '出版商' + str(id), 'desc': '内容' + str(id)}
#     return render(request, 'detail.html', {'book': book})
def detail_book(request, id):
    user = request.user.is_authenticated
    if not user:
        return redirect('/sign-in')
    book = BookData.objects.get(id=id)
    book_review = Review.objects.filter(book_id=book).order_by('-created_at')
    book_title = book.title

    if "-" in book_title:
        book_title = book_title.split('-')[0]
        book_sectitle = book.title
        book_sectitle = book_sectitle.split('-')[1]
        if "&lt;" in book_sectitle:
            book_sectitle = book_sectitle.replace("&lt;", "<")
            if "&gt;" in book_sectitle:
                book_sectitle = book_sectitle.replace("&gt;", ">")
    elif ":" in book_title:
        book_title = book_title.split(':')[0]
        book_sectitle = book.title
        book_sectitle = book_sectitle.split(':')[1]
        if "&lt;" in book_sectitle:
            book_sectitle = book_sectitle.replace("&lt;", "<")
            if "&gt;" in book_sectitle:
                book_sectitle = book_sectitle.replace("&gt;", ">")
    elif "：" in book_title:
        book_title = book_title.split('：')[0]
        book_sectitle = book.title
        book_sectitle = book_sectitle.split('：')[1]
        if "&lt;" in book_sectitle:
            book_sectitle = book_sectitle.replace("&lt;", "<")
            if "&gt;" in book_sectitle:
                book_sectitle = book_sectitle.replace("&gt;", ">")
    else:
        book_title = book_title.replace(" ", "")
        book_sectitle = ''
    if request.user.is_authenticated:
        like_exist = (Like.objects.filter(user=request.user, book=book)).exists()
        return render(request, 'detail.html',
                      {'book': book, 'reviews': book_review, 'like_exist': like_exist, 'book_title': book_title,
                       'book_sectitle': book_sectitle})
    else:
        return render(request, 'detail.html',
                      {'book': book, 'reviews': book_review, 'like_exist': False, 'book_title': book_title,
                       'book_sectitle': book_sectitle})


def insert_book_data(request):
    df = pd.read_table('book/doc2vec/book.csv', sep=',')
    count = 0
    for index in range(0, len(df['title'])):
        try:
            book_data = BookData()
            book_data.isbn = df['isbn'][index]
            book_data.title = df['title'][index]
            book_data.img_url = df['img_url'][index]
            book_data.description = df['description'][index]
            book_data.author = df['author'][index]
            book_data.price = df['price'][index]
            book_data.pub_date_2 = df['pub_date_2'][index]
            book_data.publisher = df['publisher'][index]
            book_data.save()
        except:
            count += 1
            continue

    print(count)
    return redirect('/book')


def write_review(request, id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            review = request.POST.get("my-review", "")
            book = BookData.objects.get(id=id)
            RV = Review.objects.create(
                content=review,
                writer=request.user,
                book=book
            )

            if RV:
                messages.warning(request, "成功撰写评论")

            return redirect('/book/' + str(book.id))
        else:
            messages.warning(request, "需要登录")
            return redirect('sign-in')


@login_required
def delete_review(request, id):
    rv = Review.objects.get(id=id)
    page = rv.book_id.id
    rv.delete()
    messages.warning(request, "已删除评论")
    return redirect('/book/' + str(page))


@login_required
def edit_review(request, id):
    rv = Review.objects.get(id=id)
    context = {
        'review': rv,
    }
    return render(request, 'edit.html', context)


def update(request, id):
    review = Review.objects.get(id=id)
    page = review.book_id.id
    review.content = request.POST.get('my-review')
    review.save()
    messages.warning(request, "已修改评论")
    return redirect('/book/' + str(page))


def likes(request, book_id):
    if request.user.is_authenticated:
        book = BookData.objects.get(id=book_id)
        like_exist = (Like.objects.filter(user=request.user, book=book)).exists()
        if like_exist:
            like = Like.objects.filter(
                user=request.user,
                book=book
            )
            like.delete()
            messages.warning(request, "兴趣已取消")
            return redirect('/book/' + str(book.id))
        else:
            like = Like(book=book, user=request.user)
            like.save()
            messages.warning(request, "兴趣已注册")
            return redirect('/book/' + str(book.id))

    return redirect('/sign-in')


def insert_crawling_data(request):
    bestseller = []
    book_number = 0
    page_ii = ['01', '05', '13', '15', '29', '32', '33']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    for k in page_ii:
        data = requests.get(
            f'http://www.kyobobook.co.kr/categoryRenewal/categoryMain.laf?perPage=20&mallGb=KOR&linkClass={k}&menuCode=002',
            headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')
        books = soup.select('#prd_list_type1 > li')

        for i in range(0, 20, 2):
            book_number += 1
            best_image = \
                books[i].select_one('div.thumb_cont > div.info_area > div.cover_wrap > div.cover > a > span > img')[
                    'src']
            best_title = books[i].select_one(
                'div.thumb_cont > div.info_area > div.detail > div.title > a > strong').text
            best_author = books[i].select_one(
                'div.thumb_cont > div.info_area > div.detail > div.pub_info > span.author').text
            best_publication = books[i].select_one(
                'div.thumb_cont > div.info_area > div.detail > div.pub_info > span.publication').text
            best_pub_day = books[i].select_one(
                'div.thumb_cont > div.info_area > div.detail > div.pub_info > span:nth-child(3)').text
            best_pub_day = best_pub_day.strip().replace('.', '-').replace('\t', '').replace('\r', '').replace('\n', '')
            best_price = books[i].select_one(
                'div.thumb_cont > div.info_area > div.detail > div.price > strong.sell_price').text
            best_price = best_price.replace('圆圈', '').replace(',', '')
            best_description = books[i].select_one('div.thumb_cont > div.info_area > div.detail > div.info > span').text
            bestseller.append(
                {'book_number': book_number, 'img': best_image, 'title': best_title, 'author': best_author,
                 'publication': best_publication,
                 'pub_day': best_pub_day, 'price': best_price, 'description': best_description})

    for index in range(0, len(bestseller)):
        book_data1 = BookData()
        book_data1.isbn = bestseller[index]['book_number']
        book_data1.title = bestseller[index]['title']
        book_data1.img_url = bestseller[index]['img']
        book_data1.description = bestseller[index]['description']
        book_data1.author = bestseller[index]['author']
        book_data1.price = bestseller[index]['price']
        book_data1.pub_date_2 = datetime.strptime(bestseller[index]['pub_day'][0:10], "%Y-%m-%d")
        book_data1.publisher = bestseller[index]['publication']
        book_data1.save()

    return redirect('/book')


class ProxyImageView(View):
    def get(self, req):
        url = req.GET.get('url')
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68',
            'referer': ''
        }
        if "img.dushu.com" in url:
            headers['referer'] = 'https://www.dushu.com/'

        r = requests.get(url, headers=headers, timeout=3)
        return HttpResponse(r.content, content_type=r.headers.get('Content-Type', 'image/jpeg'))
