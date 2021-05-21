'''
the function takes as the arguments the path to the folder and the path to the folder where to store new files
the function converts pdf files from path one and stores them in path two and gives a document with pdf without txt_layer
'''

!pip install pdfplumber
import os
import pdfplumber

def txt(from_PATH, to_PATH):
    os.chdir(from_PATH)
    files = os.listdir()
    l = []
    n = 0
    for file in files:
        if file.endswith("pdf"):
            pdf = pdfplumber.open(file)
            os.chdir(to_PATH) 
            n = 0
            fw = open(file[:-3]+"txt","w",encoding = "utf-8")
            for page in pdf.pages:
                text = page.extract_text()
                if type(text) == str:
                    n = n + 1
                    fw.write(text)
            fw.close() 
            if n == 0:
                l.append(file) 
                os.remove(file[:-3] + "txt")
            os.chdir(from_PATH)      
    lfile = open("pdf_without_layer.txt","w", encoding = "utf-8")
    for ll in l:
        lfile.write(ll +"\n")
    lfile.close()
