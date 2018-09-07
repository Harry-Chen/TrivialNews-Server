
# coding: utf-8

# # Initialize news

# In[1]:


import pytz
from pymongo import MongoClient
from bson.codec_options import CodecOptions
from pymongo import WriteConcern
from tqdm import tqdm

import jieba.analyse
import jieba
import jieba.posseg

from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

from config import *

# In[2]:


tz = pytz.timezone('Asia/Shanghai')
client = MongoClient(MONGO_SERVER, MONGO_PORT)
db = client['trivial_news']
categories_col = db['Categories']
channels_col = db['Channels']
statistics_col = db['Statistics']
user_col = db['Users']
news_col = db['News'].with_options(
    codec_options=CodecOptions(tz_aware=True, tzinfo=tz)
)


# In[3]:


news_all = list(news_col.find())


# In[4]:

print('Calculating search keywords for all news')
for news in tqdm(news_all):
    if 'search_keywords' not in news.keys():
        news['search_keywords'] = jieba.lcut_for_search(news['title'] + '\n' + news['summary'])


# # Update news keyword by TF-IDF

# In[5]:

print('Calculating TD-IDF index for all news')
corpus = []
for news in tqdm(news_all):
    if 'tf_idf_words' not in news.keys():
        cut = []
        for word, prop in jieba.posseg.cut(news['title'] + '\n' + news['summary']):
            if (prop[0] == 'n' or prop[0] == 'N') and prop != 'n':
                cut.append(word)
        news['td_idf_words'] = cut
    else:
        cut = news['tf_idf_words']

    corpus.append(' '.join(cut))


# In[6]:


vectorizer=CountVectorizer()
transformer=TfidfTransformer()
tfidf=transformer.fit_transform(vectorizer.fit_transform(corpus))
word=vectorizer.get_feature_names()
weight=tfidf.toarray()


# In[7]:


n = 5
for (news, w) in zip(news_all, weight):
    loc = np.argsort(-w)
    news['keywords'] = []
    for i in range(n):
        if w[loc[i]] > 0:
            news['keywords'].append(word[loc[i]])


# In[8]:


for news in tqdm(news_all):
    news_col.update_one({
        '_id': news['_id'],
    },{
        '$set': {
            'search_keywords': news['search_keywords'],
            'tf_idf_words': news['tf_ifd_words'],
            'keywords': news['keywords']
        }
    })


# # Update recommends according to news read by user

# In[9]:


id_mapping = {}
for i, news in enumerate(news_all):
    id_mapping[news['_id']] = i


# In[10]:


corpus_recommand = []
for news in tqdm(news_all):
    corpus_recommand.append(' '.join(news['search_keywords']))


# In[11]:


vectorizer_recommend=CountVectorizer()
transformer_recommend=TfidfTransformer()
tfidf_recommend=transformer_recommend.fit_transform(vectorizer_recommend.fit_transform(corpus_recommand))
word_recommend=vectorizer_recommend.get_feature_names()
weight_recommend=tfidf_recommend.toarray()


# In[12]:


def update_recommend_for_user(user_id):
    print('Calculating recommend news for user {}'.format(user_id))
    user_read = []
    for read in list(statistics_col.find({'user_id': user_id})):
        try:
            user_read.append(id_mapping[read['news_id']])
        except:
            continue

    user_tf_idf = np.zeros_like(weight_recommend[0])
    for news_i in user_read:
        user_tf_idf = user_tf_idf + weight_recommend[news_i]

    similarities = np.zeros_like(np.transpose(weight_recommend)[0])
    for i in range(len(weight_recommend)):
        similarities[i] = np.dot(user_tf_idf, weight_recommend[i])

    recommend = []
    for i in np.argsort(-similarities):
        if i not in user_read:
            recommend.append(news_all[i]['_id'])
            
    user_col.update_one({
        '_id': user_id,
    },{
        '$set': {
            'recommend': recommend[0:100]
        }
    })


# In[13]:


users = list(user_col.find())
for user in users:
    user_id = users[0]['_id']
    update_recommend_for_user(user_id)

