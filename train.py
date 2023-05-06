import os

import jieba
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_book.settings")

import django

django.setup()

from book.models import BookData

df = pd.DataFrame(list(BookData.objects.all().values()))
jieba.initialize()

df['token'] = 0
for i in range(0, len(df['title'])):
    tmp = jieba.lcut(df['title'][i])
    tmp.append('|')
    tmp2 = jieba.lcut(str(df['description'][i]))
    tmp3 = tmp + tmp2
    tokens = []
    for k in range(0, len(tmp3) - 2, 2):
        if tmp3[k] != '|':
            tokens.append(tmp3[k])

    df['token'][i] = tokens

documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(df['token'])]
model = Doc2Vec(documents, vector_size=100, window=3, epochs=10, min_count=0, workers=4)
model.save('./model.doc2vec')

# inferred_doc_vec = model.infer_vector(df['token'][100])
# most_similar_docs = model.docvecs.most_similar([inferred_doc_vec], topn=10)
#
# book_data=[]
# for index, similarity in most_similar_docs:
#     # print(f"{index}, similarity: {similarity}")
#     book_data.append({'isbn': df['isbn'][index], 'title': df['title'][index], 'img': df['img_url'][index],
#                       'description': df['description'][index], 'author': df['author'][index],
#                       'price': df['price'][index], 'pub_date': df['pub_date_2'][index],
#                       'publisher': df['publisher'][index]})
