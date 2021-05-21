!pip install pdfplumber
import os
import pdfplumber
def pdf_txt(file):
    with open(file, encoding = "utf-8") as f:
        pdf = pdfplumber.open(file)
        fw = open(file[:-3]+"txt","w",encoding = "utf-8")
        for page in pdf.pages:
            text = page.extract_text()
            fw.write(text)
        fw.close()
