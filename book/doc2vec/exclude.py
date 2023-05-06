import csv
import random
import re

import eventlet
import requests
from bs4 import BeautifulSoup

book_info_re = re.compile(r'<a href="(/book/\d+/)" title="')


def get_page_book_url(page):
    base_url = f"https://www.dushu.com/book/1008_2_0_{page}.html"
    print(f"获取{base_url}中的图书列表...")

    p = requests.get(base_url, timeout=3)
    txt = p.text
    result = book_info_re.findall(txt)
    return result


def get_book_info(url):
    base_url = "https://www.dushu.com"
    url = base_url + ('/'+url).replace('//', '/')
    print(f"正在获取{url}中的图书信息")
    resp = requests.get(url, timeout=3)
    soup = BeautifulSoup(resp.text, 'html.parser')
    book_title = soup.select_one(
        'body > div:nth-child(6) > div.bookdetails-left > div.book-title > h1').text
    img_url = soup.select_one(
        'body > div:nth-child(6) > div.bookdetails-left > div.book-pic > div.pic > img').attrs.get('src')
    price = soup.select_one('#ctl00_c1_bookleft > p > span').text[1:]
    author = soup.select_one(
        '#ctl00_c1_bookleft > table > tbody > tr:nth-child(1) > td:nth-child(2)').text.split(' ', maxsplit=1)[0]
    publisher = soup.select_one(
        '#ctl00_c1_bookleft > table > tbody > tr:nth-child(2) > td:nth-child(2)').text
    isbn = soup.select_one(
        'body > div:nth-child(6) > div.bookdetails-left > div.book-details > table > tbody > tr:nth-child(1) > td:nth-child(2)').text
    pub_date = soup.select_one(
        'body > div:nth-child(6) > div.bookdetails-left > div.book-details > table > tbody > tr:nth-child(1) > td:nth-child(4)').text
    more_info = soup.select_one(
        'body > div:nth-child(6) > div.bookdetails-left > div:nth-child(4) > div > div').text
    return isbn, book_title, author, publisher, price, img_url, more_info, pub_date


get_book_info('book/13938136/')


def save_to_csv(ran):
    csv_name = f'./book_csv_{ran[0]}-{ran[1]}.csv'
    f = open(csv_name, 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(['master_seq', 'title,author', 'publisher',
                    'price', 'img_url', 'description', 'pub_date_2'])
    for p in range(*ran):
        urls = get_page_book_url(p)
        for url in urls:
            writer.writerow(get_book_info(url))
            eventlet.sleep(random.randint(0, 5)/10)
    f.close()
    print(f"{csv_name}写入完成。")


gp = eventlet.GreenPool()
gp.spawn(save_to_csv, ran=(2, 12))
gp.spawn(save_to_csv, ran=(12, 22))
gp.spawn(save_to_csv, ran=(22, 32))
gp.spawn(save_to_csv, ran=(32, 42))
gp.spawn(save_to_csv, ran=(42, 52))
gp.spawn(save_to_csv, ran=(52, 62))
gp.spawn(save_to_csv, ran=(62, 72))
gp.spawn(save_to_csv, ran=(72, 82))
gp.spawn(save_to_csv, ran=(82, 92))
gp.spawn(save_to_csv, ran=(92, 101))
gp.waitall()
