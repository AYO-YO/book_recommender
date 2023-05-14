import csv
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_book.settings")

import django

django.setup()

from book.models import BookData

with open('./my_book.csv', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        isbn, book_title, author, publisher, price, img_url, more_info, pub_date = row
        BookData.objects.get_or_create(
            isbn=isbn,
            defaults=dict(
                title=book_title,
                author=author,
                publisher=publisher,
                price=price,
                img_url=img_url,
                pub_date_2=pub_date,
                description=more_info)
        )
print("ok")
