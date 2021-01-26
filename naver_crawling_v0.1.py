from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re
from selenium import webdriver
import psycopg2
from selenium.common.exceptions import UnexpectedAlertPresentException
from fake_useragent import UserAgent
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
# 각 크롤링 결과 저장하기 위한 리스트 선언
title_text = []
source_text = []
date_text = []
contents_text = []
result = {}

# 본문 개행 문자 제거
def contents_strip(str):
    res = str.replace("\n","")
    res = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》|┌┐─│├┤└┘┴┬]', '', res)
    return res

def crawler(maxpage, query, sort, s_date, e_date):
    try:
        print('DB 연결 전')
        conn = psycopg2.connect(host='192.168.0.135', dbname='ICT_WEB_CRW', user='postgres', password='postgrespw',
                                port='5432')
        cur = conn.cursor()
        print('DB 연결 됨')
        s_from = s_date.replace(".", "")
        e_to = e_date.replace(".", "")
        page = 1
        maxpage_t = (int(maxpage) - 1) * 10 + 1  # 11= 2페이지 21=3페이지 31=4페이지  ...81=9페이지 , 91=10페이지, 101=11페이지... 3991=400페이지 네이버는 4,000건까지 제공
        count = 0
        last = False
        while last == False:
            print('현재 크롤링 순번', page)
            #링크 초기화
            link_text = []
            sleep(2)
            url = "https://search.naver.com/search.naver?where=news&refresh_start=0&query=" + query + "&sort=" + sort + "&ds=" + s_date + "&de=" + e_date + "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + "%2Ca%3A&start=" + str(
                page)
            driver = webdriver.Chrome('chromedriver')
            driver.implicitly_wait(120)
            driver.get(url)
            response = driver.page_source
            print('첫번째 url 크롤링')
            print(url)

            # 뷰티풀소프의 인자값 지정
            soup = BeautifulSoup(response, 'html.parser')
            atags = soup.select('.info_group a')
            for atag in atags:
                if atag.text == '네이버뉴스':
                    link = atag['href']
                    if link.startswith('https://news.naver.com/main'):
                        link_text.append(link)
            print(len(link_text))

            # 마지막 페이지 주소 확인 (다음페이지 버튼이 없으면 종료페이지로 간주)
            paging = soup.find('a', class_='btn_next')
            if paging.attrs['aria-disabled'] == 'false':
                print('마지막페이지가 아닙니다')
                page += 10
            else:
                print('마지막페이지 입니다')
                last = True

            for n in range(len(link_text)):
                try:
                    driver.get(link_text[n])
                    print(link_text[n])

                except:
                    print('getting url Error = ' + link_text[n])
                    continue

                try:
                    response = driver.page_source

                except UnexpectedAlertPresentException:
                    driver.accept()
                    print("게시글이 삭제된 경우입니다.")
                    continue

                soup = BeautifulSoup(response, "html.parser")
                news_kind = soup.find('a', class_='nclicks(atp_press)').findChild()
                news_kind = news_kind['title'] #신문사 종류
                news_title = soup.find('h3', id='articleTitle').text #뉴스 제목
                news_contents = soup.find('div', id='articleBodyContents').text #뉴스 본문
                news_contents = contents_strip(news_contents)
                news_date = soup.find('span', class_='t11').text[:10]
                crawl_time = datetime.today().strftime("%Y.%m.%d")

                cur.execute("SELECT COUNT(*) FROM news_data WHERE url = %s", (link_text[n],))
                res = cur.fetchone()
                if res[0] == 0:
                    cur.execute("INSERT INTO news_data "
                                         "VALUES((select COALESCE(MAX(no), 0) + 1 as rownum from news_data), %s, %s, %s, %s, %s, %s, %s)"
                                         , [link_text[n], news_kind, news_title, news_contents, crawl_time, news_date, query])
                    conn.commit()
                    count += 1
                    print('데이터베이스 입력 완료', count, '건')

        #driver.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print('에러 발생')
        print(error)

def main():
    info_main = input("=" * 50 + "\n" + "입력 형식에 맞게 입력해주세요." + "\n" + " 시작하시려면 Enter를 눌러주세요." + "\n" + "=" * 50)

    #maxpage = input("최대 크롤링할 페이지 수 입력하시오: ")
    #query = input("검색어 입력: ")
    #sort = input("뉴스 검색 방식 입력(관련도순=0  최신순=1  오래된순=2): ")  # 관련도순=0  최신순=1  오래된순=2
    #s_date = input("시작날짜 입력(2019.01.04):")  # 2019.01.04
    #e_date = input("끝날짜 입력(2019.01.05):")  # 2019.01.05

    crawler(3991, '환경영향평가', '0', '1990.01.01', '1999.12.31')


main()