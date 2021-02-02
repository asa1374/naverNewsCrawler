# -*- coding:utf-8 -*-

import requests
import json
import traceback
import copy
import psycopg2
from bs4 import BeautifulSoup
import asyncio
import aiohttp
#from utils.time import now_ms_ts

data = {
    "byLine": "",
    "categoryCodes": [],
    "dateCodes": [],
    "endDate": "1999-12-31",  # 끝나는 날짜
    "incidentCodes": [],
    "indexName": "news",
    "isNotTmUsable": 'false',
    "isTmUsable": 'false',
    "mainTodayPersonYn": "",
    "networkNodeType": "",
    "newsIds": None,
    "providerCodes": [],
    "resultNumber": 10,
    "searchFilterType": "1",
    # "searchKey": "삼성 최순실",
    # 검색식
    "searchKey": "환경영향평가",
    "searchKeys": [{}],
    # "searchKeys": [{"orKeywords": ["삼성, 신세계, 현대, SK,LG"]}],
    "searchScopeType": "1",  # 1: 제목검색 2: 제목+내용검색
    "searchSortType": "date",
    "sortMethod": "date",
    "startDate": "1990-01-01",  # 시작날짜
    "startNo": 1,
    "topicOrigin": ""
}

result_url = "https://www.kinds.or.kr/api/news/search.do"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Content-Type": "application/json;charset=UTF-8",
    "Host": "www.kinds.or.kr",
    "Origin": "http://www.kinds.or.kr",
    "Referer": "http://www.kinds.or.kr/v2/news/index.do",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

print(json.dumps(data, ensure_ascii=False))
body = json.dumps(data, ensure_ascii=False).encode('utf-8')
print(headers)
loop = asyncio.get_event_loop()
count = 0


async def fetch_post(session, url, body):
    try:
        async with session.post(url, json=body, headers=headers) as response:
            res = await response.json()
            return res
    except Exception as e:
        print('e={}, trace={}'.format(repr(e), traceback.format_exc()))


async def fetch_get(session, url, result):
    try:
        async with session.post(url, headers=headers) as response:
            res = await response.json()
            return res
    except Exception as e:
        print('e={}, trace={}'.format(repr(e), traceback.format_exc()))
        print(result)


def read_news_detail(session, res):
    before_read_list = datetime.now()
    tasks = []

    for result in res['resultList']:
        news_url = f"https://www.bigkinds.or.kr/news/detailView.do?docId={result['NEWS_ID']}&returnCnt=1&sectionDiv=1000"
        tasks.append(fetch_get(session, news_url, result))
        global count
        count = count + 1
        if count % 1000 == 0:
            print(count, '개의 기사를 수집했습니다')
    return tasks
    print('Every 10 post', datetime.now() - before_read_list)


async def post_news_list():
    tasks = []
    async with aiohttp.ClientSession() as session:
        first_call = await fetch_post(session, result_url, data)
        print('totalCount: ', first_call['totalCount'])
        for index in range(1, int((first_call['totalCount'] + 9) / 10)):
            data['startNo'] = index
            temp_data = copy.copy(data)
            tasks.append(fetch_post(session, result_url, temp_data))

        before_read_news_detail = datetime.now()
        news_list = await asyncio.gather(*tasks)
        print('뉴스 리스트 호출 시 걸린 시간 :', datetime.now() - before_read_news_detail, 'ms')
        detail_tasks = []
        for news in news_list:
            detail_list = read_news_detail(session, news)
            detail_tasks.extend(detail_list)

        news_detail_list = await asyncio.gather(*detail_tasks)

        print('전체 호출 시 걸린 시간 :', datetime.now() - before_read_news_detail, 'ms')

        return news_detail_list


#import pymysql
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

import os

# Establish a MySQL connection
# db_url = os.environ['192.168.0.135']
# db_user = os.environ['postgres']
# db_password = os.environ['postgrespw']
# db_port = int(os.environ['5432'])
# db_name = os.environ['ICT_WEB_CRW']

# if os.environ['DB_USE_LOCAL'] == 'FALSE':
#     db_url = os.environ['DB_URL']
#     db_user = os.environ['DB_USER']
#     db_password = os.environ['DB_PASSWORD']
#     db_port = os.environ['DB_PORT']
#     db_name = os.environ['DB_NAME']
#     import sqlalchemy
#
#     engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(
#         drivername='mysql+pymysql',
#         host=db_url,
#         username=db_user,
#         password=db_password,
#         database=db_name,
#         query={
#             'unix_socket': '/cloudsql/{}'.format("manjum:asia-northeast2:manjum"),
#             'charset': 'utf8mb4'
#         }
#     ),
#     )
#     database = engine.connect()
# else:
#     database = pymysql.connect(host=db_url, port=db_port, user=db_user, passwd=db_password, db='mysql')

database = psycopg2.connect(host='192.168.0.135', dbname='ICT_WEB_CRW', user='postgres', password='postgrespw',
                                port='5432')
# Get the cursor, which is used to traverse the database, line by line
cursor = database.cursor()
print(f'Now you gonna Connect to 192.168.0.135 db 연결됨')
# Create the INSERT INTO sql query
# query = """INSERT INTO manjum.news_data (id, news_date, media_name, writer, title, key1, key2, key3, acident1, acident2, acident3, `character`, location, agency, keyword, keyword_export, url, exception, body) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE valid = VALUES(valid) + 1"""
query = """INSERT INTO news_data VALUES((select COALESCE(MAX(no), 0) + 1 as rownum from news_data), %s, %s, %s, %s, %s, %s, %s)"""


def insert_news_to_db(news_detail_list):
    before_query = datetime.now()

    print(len(news_detail_list))

    for detail in news_detail_list:
        # print(detail)
        if detail['detail'] == "None":
            continue
        detail_data = detail['detail']
        # print(detail_data['TITLE'])
        id = detail_data['NEWS_ID']
        news_date = detail_data['DATE']
        media_name = detail_data['PROVIDER']
        writer = detail_data['BYLINE']
        title = detail_data['TITLE']
        key = detail_data['CATEGORY'].split('|')
        key1 = key[0].replace("</font>", "").replace("<font color=Gray>", "") if len(key) > 0 else ''
        key2 = key[1].replace("</font>", "").replace("<font color=Gray>", "") if len(key) > 1 else ''
        key3 = key[2].replace("</font>", "").replace("<font color=Gray>", "") if len(key) > 2 else ''
        acident = detail_data['CATEGORY_INCIDENT'].split('|')
        acident1 = acident[0].replace("</font>", "").replace("<font color=Gray>", "") if len(acident) > 0 else ''
        acident2 = acident[1].replace("</font>", "").replace("<font color=Gray>", "") if len(acident) > 1 else ''
        acident3 = acident[2].replace("</font>", "").replace("<font color=Gray>", "") if len(acident) > 2 else ''
        character = detail_data['TMS_NE_PERSON']
        location = detail_data['TMS_NE_LOCATION']
        agency = detail_data['TMS_NE_ORGANIZATION']
        keyword = detail_data['TMS_RAW_STREAM']
        keyword_export = detail_data['TMS_NE_STREAM']
        url = detail_data['PROVIDER_LINK_PAGE']
        exception = ''
        body = detail_data['CONTENT']
        crawl_time = datetime.today().strftime("%Y.%m.%d")

        values = (url, media_name, title, body, crawl_time, news_date, data.get("searchKey"))

        if id == '':
            print(values)
        try:
            cursor.execute(query, values)
        except Exception as e:
            print('e={}, trace={}'.format(repr(e), traceback.format_exc()))

    # Close the cursor
    cursor.close()
    # Commit the transaction
    database.commit()

    # Close the database connection
    database.close()

    print('db insert time :', datetime.now() - before_query, 'ms')


async def print_when_done(tasks):
    for res in asyncio.as_completed(tasks):
        news_detail_list = await res
        insert_news_to_db(news_detail_list)


coros = [post_news_list()]
loop = asyncio.get_event_loop()
loop.run_until_complete(print_when_done(coros))
loop.close()