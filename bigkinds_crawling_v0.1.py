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

# def setSearchText(searchText):
#     text = driver.find_element_by_id("total-search-key")
#     text.send_keys(searchText)
#
# def setSearchDate(beginDate,endDate):
#     searchBeginDate = driver.find_element_by_id("search-begin-date")
#     searchEndDate = driver.find_element_by_id("search-end-date")
#     searchBeginDate.send_keys(beginDate)
#     searchEndDate.send_keys(endDate)


def crawler(maxpage, query, sort, s_date, e_date):

    print('DB 연결 전')
    conn = psycopg2.connect(host='192.168.0.135', dbname='ICT_WEB_CRW', user='postgres', password='postgrespw',
                            port='5432')
    cur = conn.cursor()
    print('DB 연결 됨')

    last = False
    #링크 초기화
    link_text = []
    sleep(2)

    url = "https://www.bigkinds.or.kr/"
    driver = webdriver.Chrome('chromedriver')
    driver.get(url)
    #sleep(3)
    popclose = driver.find_element_by_xpath('// *[ @ id = "popup-dialog-65"] / div[2] / div / div[2] / button')
    dateclick = driver.find_element_by_id("date-filter-btn")
    dateclick.click()
    searchBeginDate = driver.find_element_by_xpath('// *[ @ id = "search-begin-date"]')
    searchBeginDate.clear()
    searchBeginDate
    #searchBeginDate.send_keys("1990-01-01")
    searchEndDate = driver.find_element_by_id("search-end-date")
    searchEndDate.send_keys("1999-12-31")
    text = driver.find_element_by_id("total-search-key")
    text.send_keys("환경영향평가")
    print('환경영향평가 입력')

    #searchBeginDate = driver.find_element_by_id("search-begin-date")


    newsSearchBtn = driver.find_element_by_xpath('//*[@id="news-search-form"]/div/div/div/div[1]/span/button')
    newsSearchBtn.click()

    driver.implicitly_wait(120)
    response = driver.page_source
    print('첫번째 url 크롤링')

    # 뷰티풀소프의 인자값 지정
    soup = BeautifulSoup(response, 'html.parser')
    search_text = soup.select('.news-item__title')
    print('뉴스 제목 ::: ',search_text)


    # 마지막 페이지 주소 확인 (다음페이지 버튼이 없으면 종료페이지로 간주)
    # paging = soup.find('a', class_='btn_next')
    # if paging.attrs['aria-disabled'] == 'false':
    #     print('마지막페이지가 아닙니다')
    #     page += 10
    # else:
    #     print('마지막페이지 입니다')
    #     last = True


    #driver.close()
    conn.close()


def main():
    #info_main = input("=" * 50 + "\n" + "입력 형식에 맞게 입력해주세요." + "\n" + " 시작하시려면 Enter를 눌러주세요." + "\n" + "=" * 50)

    #maxpage = input("최대 크롤링할 페이지 수 입력하시오: ")
    #query = input("검색어 입력: ")
    #sort = input("뉴스 검색 방식 입력(관련도순=0  최신순=1  오래된순=2): ")  # 관련도순=0  최신순=1  오래된순=2
    #s_date = input("시작날짜 입력(2019.01.04):")  # 2019.01.04
    #e_date = input("끝날짜 입력(2019.01.05):")  # 2019.01.05

    crawler(3991, '환경영향평가', '0', '1990.01.01', '1999.12.31')


main()