# -*- coding: utf-8 -*-
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import re
from selenium import webdriver
import psycopg2
from webdriver_manager.chrome import ChromDriverManger

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
< naver 뉴스 검색시 리스트 크롤링하는 프로그램 > _select사용
- 크롤링 해오는 것 : 링크,제목,신문사,날짜,내용요약본
- 날짜,내용요약본  -> 정제 작업 필요
- 리스트 -> 딕셔너리 -> df -> 엑셀로 저장 
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# 각 크롤링 결과 저장하기 위한 리스트 선언
title_text = []
link_text = []
source_text = []
date_text = []
contents_text = []
result = {}

# 엑셀로 저장하기 위한 변수
RESULT_PATH = 'C:/dev/python/conda/crawling/'  # 결과 저장할 경로
now = datetime.now()  # 파일이름 현 시간으로 저장하기


# 날짜 정제화 함수
def date_cleansing(test):
    try:
        # 지난 뉴스
        # 머니투데이  10면1단  2018.11.05.  네이버뉴스   보내기
        pattern = '\d+.(\d+).(\d+).'  # 정규표현식

        r = re.compile(pattern)
        match = r.search(test).group(0)  # 2018.11.05.
        date_text.append(match)

    except AttributeError:
        # 최근 뉴스
        # 이데일리  1시간 전  네이버뉴스   보내기
        pattern = '\w* (\d\w*)'  # 정규표현식

        r = re.compile(pattern)
        match = r.search(test).group(1)
        # print(match)
        date_text.append(match)

# 본문 개행 문자 제거
def contents_strip(str):
    res = str.replace("\n","")
    res = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》|┌┐─│├┤└┘┴┬]', '', res)
    return res

# 내용 정제화 함수
def contents_cleansing(contents):
    first_cleansing_contents = re.sub('<dl>.*?</a> </div> </dd> <dd>', '',
                                      str(contents)).strip()  # 앞에 필요없는 부분 제거
    second_cleansing_contents = re.sub('<ul class="relation_lst">.*?</dd>', '',
                                       first_cleansing_contents).strip()  # 뒤에 필요없는 부분 제거 (새끼 기사)
    third_cleansing_contents = re.sub('<.+?>', '', second_cleansing_contents).strip()
    contents_text.append(third_cleansing_contents)
    # print(contents_text)


def crawler(maxpage, query, sort, s_date, e_date):
    try:
        conn = psycopg2.connect(host='192.168.0.135', dbname='ICT_WEB_CRW', user='postgres', password='postgrespw', port='5432')
        cur = conn.cursor()
        link = 'https://news.naver.com/main/read.nhn?mode=LSD&mid=sec&sid1=102&oid=001&aid=0004520958'
        url = link
        sleep(0.1)
        driver = webdriver.Chrome('chromedriver')
        driver.get(url)

        news_kind = driver.find_element_by_class_name("press_logo").find_element_by_tag_name('a').find_element_by_tag_name('img').get_attribute('title')
        news_title = driver.find_element_by_id("articleTitle").text
        news_contents = driver.find_element_by_id("articleBodyContents").text
        news_contents = contents_strip(news_contents)

        news_date = driver.find_element_by_class_name("t11").text[:10]
        crawl_time = datetime.today().strftime("%Y.%m.%d")

        print(news_title)  # 제목
        print(news_contents)  # 제목
        cur.execute("INSERT INTO news_data "
                     "VALUES((select COALESCE(MAX(no), 0) + 1 as rownum from news_data), %s, %s, %s, %s, %s, %s, %s)"
                     , [link, news_kind, news_title, news_contents, crawl_time, news_date, query])

        conn.commit()
        driver.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print('에러 발생')
        print(error)


def main():
    info_main = input("=" * 50 + "\n" + "입력 형식에 맞게 입력해주세요." + "\n" + " 시작하시려면 Enter를 눌러주세요." + "\n" + "=" * 50)

    maxpage = input("최대 크롤링할 페이지 수 입력하시오: ")
    query = input("검색어 입력: ")
    #sort = input("뉴스 검색 방식 입력(관련도순=0  최신순=1  오래된순=2): ")  # 관련도순=0  최신순=1  오래된순=2
    #s_date = input("시작날짜 입력(2019.01.04):")  # 2019.01.04
    #e_date = input("끝날짜 입력(2019.01.05):")  # 2019.01.05

    crawler(1, '환경영향평가', '0', '1990.01.01', '1999.12.31')


main()