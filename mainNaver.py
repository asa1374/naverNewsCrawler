from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re
from selenium import webdriver
import psycopg2
from fake_useragent import UserAgent
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
# 각 크롤링 결과 저장하기 위한 리스트 선언
title_text = []
link_text = []
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
        while page <= maxpage_t:
            print('현재 크롤링 순번', page)
            sleep(20)
            url = "https://search.naver.com/search.naver?where=news&refresh_start=0&query=" + query + "&sort=" + sort + "&ds=" + s_date + "&de=" + e_date + "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + "%2Ca%3A&start=" + str(
                page)
            #print('url', url)
            #ua = UserAgent()
            #headers = {'User-Agent': ua.random}
            response = requests.get(url, verify=False) #headers=headers,
            print('첫번째 url 크롤링')
            html = response.text

            # 뷰티풀소프의 인자값 지정
            soup = BeautifulSoup(html, 'html.parser')

            atags = soup.select('.info')
            for atag in atags:
                if atag.text == '네이버뉴스':
                    try:
                        print('두번째 url 크롤링')
                        link_text.append(atag['href'])  # 링크주소
                        link = atag['href']
                        url = link
                        sleep(20)
                        driver = webdriver.Chrome('chromedriver')
                        driver.implicitly_wait(120)
                        driver.get(url)
                        try:
                            element = WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located(((By.XPATH, '//*[@id="main_content"]/div[1]/div[1]/a/img'))))
                            print('로고 찾고 페이지 로딩 완료')
                            news_kind = driver.find_element_by_class_name("press_logo").find_element_by_tag_name('a').find_element_by_tag_name('img').get_attribute('title')
                            news_title = driver.find_element_by_id("articleTitle").text
                            news_contents = driver.find_element_by_id("articleBodyContents").text
                            news_contents = contents_strip(news_contents)

                            news_date = driver.find_element_by_class_name("t11").text[:10]
                            crawl_time = datetime.today().strftime("%Y.%m.%d")
                            print(news_title)  # 제목

                            cur.execute("INSERT INTO news_data "
                                        "VALUES((select COALESCE(MAX(no), 0) + 1 as rownum from news_data), %s, %s, %s, %s, %s, %s, %s)"
                                        , [link, news_kind, news_title, news_contents, crawl_time, news_date, query])

                            conn.commit()
                            count += 1
                            print('데이터베이스 입력 완료', count, '건')

                            #print(link) #뉴스경로
                            #print(news_kind) #신문사 종류
                            #print(news_title) #제목
                            #print(news_contents) #본문
                            #print(crawl_time) #크롤링시간 ex)2020.12.30
                            #print(news_date) #기사 등록 시간 ex)2020.12.30
                            #print(query)

                            driver.close()
                        except Exception as ee:
                            print('페이지 로드 안됨')
                            print(ee)
                            continue
                    except Exception as e:
                        print('신문사 종류 및 본문 내용 크롤링 실패')
                        print(e)
                        continue
            page += 10
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