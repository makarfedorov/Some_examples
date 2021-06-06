'''
Датасет московского зоопарка в формате json
Код выделяет семейство, отряд, класс и тип из поля Info (в исходном файле этот кусок не стандартизованн, может присуствовать семейство и отряд, может семейство и класс и т.д.)
Также код выделяет Ареал обитания. В исходном файле это неструктированно, поэтому извлечение делается с помощью регулярных выражений. В конце изменения записываются в новый json
'''

import requests
import json
import re

api_link = 'https://apidata.mos.ru/v1/datasets/{dataset_id}/rows?api_key={key}'
data_id = '3286'
my_api_key = "b98664accaf33bb1a34c9f77c72f191f"
link = api_link.format (dataset_id = data_id, key = my_api_key)
zoo_data = requests.get(link).text
json_data = json.loads (zoo_data)
animal_type = {"Семейство":"Family","Отряд":"Order","Класс":"Class", "Тип": "Phylum"}
pattern_area = "((О|о)бита(е|ю)т|(З|з)авезен(а|ы){0,1}|(Р|р)аспростран(ё|е)н(а|ы){0,1}|(Э|э)(н){0,1}дем|(А|а)реал(а){0,1}|(Н|н)аселя(е|ю)т|Гнезд(и|я)тся|Встречается|(П|п)ород(а|ы)|(В|в)ыведен(а){0,1}|(Т|т)ерритори(и|я|ю)|Америки|Азии|Род(ина|ом))" 
for item in json_data:
    Info = item["Cells"]["Info"]
    Info_1 = Info.split(".")
    Info_2 = Info_1[:2]
    for i in Info_2:
        for a in animal_type:
            if a in i:
                pattern = a + "(:| - | : |\s)"
                I = re.sub(pattern, r"",i)  
                I = re.sub(r"\s+(.*)",r"\1",I)  
                item["Cells"][animal_type[a]] = I
            elif "Cемейство" in i:
                pattern = a + "(:| - | : |\s)"
                I = re.sub(pattern, r"",i)  
                I = re.sub(r"\s+(.*)",r"\1",I) 
                item["Cells"][animal_type["Семейство"]] = I                             
    Region = ""            
    for n, i in enumerate(Info_1):
        i = re.sub(r"(\n|\s\n)", r"", i)
        if re.search("((\s[о]$|\s[р]$))|((Ареал обитания.|Естественный ареал.))", i):
            Region = Region + i + "." + Info_1[n+1] + "." 
        elif re.search(pattern_area, i):
            Region = Region + i + "."                        
    Region = re.sub(r"(\n|\s+\n)", r"", Region)                      
    item["Cells"]["Region"] = Region
   

with open ('zoo_data.json', 'w', encoding='utf-8') as json_file:
  json_file.write (json.dumps(json_data, ensure_ascii=False, indent = 4))
