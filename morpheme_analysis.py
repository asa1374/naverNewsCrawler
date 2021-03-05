# -*- coding:utf-8 -*-
import psycopg2
from konlpy.tag import Okt
import re
from collections import Counter
from wordcloud import WordCloud

import nltk


#db 연결
database = psycopg2.connect(host='192.168.0.135', dbname='ICT_WEB_CRW', user='postgres', password='postgrespw',
                                port='5432')
cursor = database.cursor()

# 본문내용 불러오기
str1 = """select contents from news_data_sum_1990_1999 where "no" = 3 """
cursor.execute(str1)
res1 = cursor.fetchone()

print(res1[0])
nobr = re.sub('<br/>', '', res1[0])

okt = Okt()
#단어만 추출
#token_ko = okt.nouns(res1[0])
#어절만 추출
#okt.phrases(res1[0])

token_ko = okt.nouns(res1[0])
count = Counter(token_ko)


noun_list = count.most_common(10000)
print(noun_list)
# for v in noun_list:
#     print(v)
    # res = v[0] + " (" + str(v[1]) + ")"




#
# wc = WordCloud(font_path='C:\\Windows\\Fonts\\08SeoulNamsanB_0.ttf', \
#                background_color="white", \
#                width=1000, \
#                height=1000, \
#                max_words=100, \
#                max_font_size=300)



# Commit the transaction
#database.commit()

# Close the database connection
database.close()
