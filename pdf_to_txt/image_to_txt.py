'''
the function converts pdf files into txt using ocr. 
To use the function you need to download rus.traineddata from: 
https://github.com/tesseract-ocr/tessdata/blob/master/rus.traineddata
'''

!apt-get install poppler-utils 
!apt install tesseract-ocr
!pip install pytesseract
!pip install pdf2image
from PIL import Image 
import pytesseract 
import sys 
from pdf2image import convert_from_path 
import os

def pdf_image(PDF_File, dpi): 
    pages = convert_from_path(PDF_File, dpi) 
    image_counter = 1
  
    for page in pages: 
        filename = "page_"+str(image_counter)+".jpg"
        page.save(filename, 'JPEG') 
        image_counter = image_counter + 1
    
    filelimit = image_counter-1
  
    outfile = "out_text.txt"
  
    f = open(outfile, "a") 
  
    for i in range(1, filelimit + 1):  
        filename = "page_"+str(i)+".jpg"   
        text = str(((pytesseract.image_to_string(Image.open(filename), lang="rus")))) 
        text = text.replace('-\n', '')     
        f.write(text) 

    f.close() 
