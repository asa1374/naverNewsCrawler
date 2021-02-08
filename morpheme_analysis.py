# -*- coding:utf-8 -*-
import psycopg2
# str1 = 사업구분과 평가유형을 분류하여 업데이트 해야 할 첫번째 구분이 됨
# res1 = 사업구분 및 평가유형의 결과를 받아옴

#db 연결
database = psycopg2.connect(host='192.168.0.135', dbname='ICT_WEB_CRW', user='postgres', password='postgrespw',
                                port='5432')
cursor = database.cursor()

# 본문내용 불러오기
str1 = """select contents from news_data_sum_1990_1999 where "no" = 1 """
cursor.execute(str1)
res1 = cursor.fetchall()
print(res1)


# Commit the transaction
#database.commit()

# Close the database connection
database.close()
