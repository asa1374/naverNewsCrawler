import PyPDF2
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import pdfplumber
import pandas as pd

pdf_path='air.pdf'

def pdf2txt(pdf_file):
    fp = open(pdf_file, 'rb')
    total_pages = PyPDF2.PdfFileReader(fp).numPages

    page_text = {}
    for page_no in range(total_pages):
        rsrcmgr = PDFResourceManager()

        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = open(pdf_file, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = None
        maxpages = 0
        caching = True
        pagenos = [page_no]

        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,
                                      caching=caching, check_extractable=True):
            interpreter.process_page(page)

        page_text[page_no] = retstr.getvalue()

        fp.close()
        device.close()
        retstr.close()
    return page_text

def pdftoexcel(page_num):
    pdf = pdfplumber.open("air.pdf")
    p0 = pdf.pages[page_num]
    pd.set_option('display.max_rows', 20)
    pd.set_option('display.max_columns', 20)
    table2df = lambda table: pd.DataFrame(table[1:], columns=table[0])
    tables = table2df(p0.extract_table())

    tables.to_excel(excel_writer='sample' + str(page_num) + '.xlsx')  # 엑셀로 저장
    return 0

page = 0
text = pdf2txt(pdf_path)
for item in range(len(text)):
    test = text[item][:-1].find('<표  7.2.2-6>')
    if test != -1:
        print("있다")
        print(item)
        pdftoexcel(item)
    else:
        print("없다")