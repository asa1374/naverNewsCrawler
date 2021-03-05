import os
from tabula import read_pdf
import pdfplumber
import pandas as pd
import numpy as np

# pdf = pdfplumber.open("air.pdf")
# p0 = pdf.pages[6]
# pd.set_option('display.max_rows', 20)
# pd.set_option('display.max_columns', 20)
# table2df = lambda table: pd.DataFrame(table[1:], columns=table[0])
# tables = table2df(p0.extract_table())
# # print(tables)
#
# tables.to_excel(excel_writer='sample3.xlsx')  # 엑셀로 저장

import PyPDF2
pdfFileObj= open("air.pdf", 'rb')
pdfReader= PyPDF2.PdfFileReader(pdfFileObj)
pageObj= pdfReader.getPage(0)
print(pageObj.extractText())