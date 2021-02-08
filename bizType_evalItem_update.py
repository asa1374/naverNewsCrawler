# -*- coding:utf-8 -*-
import psycopg2
# str1 = 사업구분과 평가유형을 분류하여 업데이트 해야 할 첫번째 구분이 됨
# res1 = 사업구분 및 평가유형의 결과를 받아옴

#db 연결
database = psycopg2.connect(host='192.168.0.135', dbname='ICT_WEB_CRW', user='postgres', password='postgrespw',
                                port='5432')
cursor = database.cursor()

# 1~17까지는 사업구분
# 18~38까지는 평가유형
#str1 = """select "no","name" from com_code where cast("no" as smallint) > 17 """
str1 = """select "no","name" from com_code """
cursor.execute(str1)
res1 = cursor.fetchall()
# print(res1)

for res in res1:
    # print(res[1])

    str2 = """select a."no",b."name" from news_data_sum_1990_1999_temp2 a  
                left join (select ct.searchkeyword,cc."name" from com_text ct,com_code cc where cast(ct.com_code_no as smallint) = cc."no")
                 b on a.contents like CONCAT('%',b.searchkeyword,'%')
                where b."name" = '"""+res[1]+"""'  group by a."no",b."name" """
    value = res[1]
    cursor.execute(str2)
    res2 = cursor.fetchall()
    # print(res2)
    for res3 in res2:
        res3str = str(res3[0])
        # 각 사업유형,평가항목을 조회하여 /1.~~를 업데이트 하기 위해 기존 사업유형및 평가항목을 조회
        if res[0] <= 17:
            str3 = """select dbgud from news_data_sum_1990_1999_temp2 where dbgud like CONCAT('%','"""+res[1]+"""','%') and "no" = cast("""+res3str+""" as smallint)  """
        else:
            str3 = """select vudrkgkdahr from news_data_sum_1990_1999_temp2 where vudrkgkdahr like CONCAT('%','""" + res[
                1] + """','%') and "no" = cast(""" + res3str + """ as smallint)  """
        cursor.execute(str3)
        res4 = cursor.fetchall()
        if not res4:
            # 각 사업유형,평가항목의 /1.~~~2.~~~업데이트 쿼리
            if res[0] <= 17:
                str4 = """update news_data_sum_1990_1999_temp2
                        set dbgud = CONCAT(dbgud,'/""" + res[1] + """') 
                        where "no" = cast("""+res3str+""" as smallint)"""
            else:
                str4 = """update news_data_sum_1990_1999_temp2
                                        set vudrkgkdahr = CONCAT(vudrkgkdahr,'/""" + res[1] + """') 
                                        where "no" = cast(""" + res3str + """ as smallint)"""
            cursor.execute(str4)
        else:
            continue
#각 사업유형,평가항목의 첫번째문자 "/" 제거
str5 = """update public.news_data_sum_1990_1999_temp2
        set dbgud=substring(dbgud,2)
            ,vudrkgkdahr=substring(vudrkgkdahr,2)"""
cursor.execute(str5)

# Commit the transaction
#database.commit()

# Close the database connection
database.close()
