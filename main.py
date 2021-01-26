import requests
from bs4 import BeautifulSoup
import openpyxl
from konlpy.tag import Okt
from collections import Counter
import pytagcloud
import webbrowser

if __name__ == '__main__':
    code_list = ['ME2017B004','GG2018A003','GG2015B003','GG2011B008']
    contents = ""
    for i in code_list:
        url = "https://eiass.go.kr/ICT/enImpactAssessment/bizOpinionPop.do?eiaCode="+i+"&eiaGbCd=1"
        heml2 = requests.get(url).text
        soup = BeautifulSoup(heml2,"html.parser")
        #사업명
        titles = soup.select(".title_wrap h2")
        for ind in titles:
            title =ind.text

        content_1 = soup.select('div[id=sub01_02_pop02_tab01] > div > ul > li')[0].text
        contents += content_1
        content_2 = soup.select("div[id=sub01_02_pop02_tab02] > div > ul > li:nth-of-type(1) > p")[0].text
        contents += content_2
        content_3 = soup.select('div[id=sub01_02_pop02_tab02] > div > ul > li:nth-of-type(2) > p')[0].text
        contents += content_3
        content_4 = soup.select('div[id=sub01_02_pop02_tab02] > div > ul > li:nth-of-type(3) > p')[0].text
        contents += content_4
        content_5 = soup.select('div[id=sub01_02_pop02_tab02] > div > ul > li:nth-of-type(4) > p')[0].text
        contents += content_5
        content_6 = soup.select('div[id=sub01_02_pop02_tab02] > div > ul > li:nth-of-type(5) > p')[0].text
        contents += content_6
        content_7 = soup.select('div[id=sub01_02_pop02_tab02] > div > ul > li:nth-of-type(6) > p')[0].text
        contents += content_7
        content_8 = soup.select('div[id=sub01_02_pop02_tab02] > div > ul > li:nth-of-type(7) > p')[0].text
        contents += content_8


    okt = Okt()
    text_data = []
    ex_nouns = okt.nouns(contents)
    print(contents)

    for text in ex_nouns:
        if text != '및' and text != '를' and text != '함' and text != '등':
            text_data.append(text)

    word_count = {}

    for noun in text_data:
        word_count[noun] = word_count.get(noun,0) + 1

    counter = Counter(word_count)
    top10 = counter.most_common(10)
    word_count_list = pytagcloud.make_tags(top10,maxsize=80)
    pytagcloud.create_tag_image(word_count_list,
                                'wordcloud.jpg',  # 생성될 시각화 파일 이름
                                size=(900, 600),  # 사이즈
                                fontname='Nanum Gothic',  # 한글 시각화를 위해 새로 추가했던 폰트 이름
                                rectangular=False)
    webbrowser.open('wordcloud.jpg')