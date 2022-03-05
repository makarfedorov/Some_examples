import urllib.request
import bs4
from bs4 import BeautifulSoup
import requests
import re
from prereform2modern import Processor
from lxml import etree
import dateparser



ns = {None:"http://www.tei-c.org/ns/1.0", "xi": "http://www.w3.org/2001/XInclude"}

volume_id = {47:["h000011001", "h000011002"], 48:["h000011001", "h000011013"],
             49:["h000010001", "h000010005"], 50:["h000010001", "h000010003"],
             51:["h000008001","h000008004"], 52:["h000008001", "h000008006"],
             53:["h000010001","h000010005"], 54:["h000011001", "h000011009"],
             55:["h000011001","h000011009"], 56:["h000010001", "h000010009"],
             57:["h000011001", "h000011003"], 58:["h000012001", "h000012014"]}

tag_dict = {"h2":"head", "h3":"head", "tr":"row", "td":"cell", "em":"hi", "p":"p", "span":"hi"}
atr_dict = {"class":"rend"}
def get_html(url):
    html = requests.get(url).text
    return html 
def get_img(url_img):
    url_img = f"{url}{url_img}"
    img = requests.get(url_img).content
    
    return img 

def TEI_template():
    """ 
    Function creates TEI (XML) template for Tolstoy's notebooks
    :param: None
    :return: lxml.etree._Element
    """
    root = etree.Element("TEI", nsmap = ns)
    teiHeader = etree.Element("teiHeader")
    root.append(teiHeader)
    fileDesc = etree.Element("fileDesc")
    teiHeader.append(fileDesc)
    titleStmt = etree.Element("titleStmt")
    fileDesc.append(titleStmt)
    title = etree.Element("title")
    titleStmt.append(title)
    title.text = " "
    publicationStmt = etree.Element("publicationStmt")
    fileDesc.append(publicationStmt)
    publisher = etree.Element("publisher")
    publicationStmt.append(publisher)
    publisher.text = "TolstoyLab"
    sourceDesc = etree.Element("sourceDesc")
    fileDesc.append(sourceDesc)
    biblStruct = etree.Element("biblStruct")
    sourceDesc.append(biblStruct)
    analytic = etree.Element("analytic")
    biblStruct.append(analytic)
    author = etree.Element("author")
    analytic.append(author)
    author.text = "Толстой Л.Н."
    monogr = etree.Element("monogr")
    biblStruct.append(monogr)
    imprint = etree.Element("imprint")
    monogr.append(imprint)
    publisher_imprint = etree.Element("publisher")
    imprint.append(publisher_imprint)
    publisher_imprint.text = 'Государственное издательство "Художественная литература"'
    pubPlace = etree.Element("pubPlace")
    monogr.append(pubPlace)
    pubPlace.text = "Москва"
    series = etree.Element("series")
    biblStruct.append(series)
    level_s_title = etree.Element("title")
    series.append(level_s_title)
    level_s_title.set("level", "s")
    level_s_title.text = "Л.Н. Толстой. Полное собрание сочинений"
    biblScope = etree.Element("biblScope")
    series.append(biblScope)
    biblScope.set("unit", "vol")
    biblScope.text = " "
    encodingDesc = etree.Element("encodingDesc")
    teiHeader.append(encodingDesc)
    tagsDecl = etree.Element("tagsDecl")
    encodingDesc.append(tagsDecl)
    return root
  
  
def common_start(first_id, last_id):
    """ 
    returns the longest common substring from the beginning of first id
    and last id
     """
    def _iter():
        for a, b in zip(first_id, last_id):
            if a == b:
                yield a
            else:
                return

    return ''.join(_iter()), len(first_id)
 
def get_html_dict(soup, first_id, last_id):
    common_id, lenght = common_start(first_id, last_id)
    html_dict = {}
    l = list()
    html = soup.findAll(id=re.compile(common_id))
    for n, id in enumerate(html):
        if len(id.get("id")) == lenght and len(l) > 0:
            html_dict[l[0]] = l
            l = list()
            l.append(id.get("id"))
                
        else:
            l.append(id.get("id"))
        if n + 1 == len(html):
            html_dict[l[0]] = l
        
    return html_dict 

def get_title(soup, id):
    html_id = soup.find(id=id) 
    title_html = html_id.find("h2")
    if title_html: 
        pass
    else:
        title_html = html_id.find_next_sibling("div").find("h2")
    return title_html
  
def id_to_html(soup, id):
    html = soup.find(id=id)
    if not html.find("p"):
        html = html.find_next_sibling(class_="section")
    return html  

def subsitute_notes(soup, p):
    for note in p.findAll("a", {"type":"note"}):
        note_number = note.get("href")[1::]
        back_note = soup.find(id=note_number)
        back_note_text = back_note.find("p").get_text()
        note.string = back_note_text
    return p

def subsitute_notes(soup, p):
    return p
def del_tag(text):
    delete_pattern = re.compile("&lt;(.*?)&gt;")
    text = delete_pattern.sub("<del>\g<1></del>", text)
    return text

def markup_choices_for_prereform_spelling(text):
    split_pattern = re.compile(r'(<choice.*?>.*?</choice>)')
    tokens = split_pattern.split(text)
    # print(tokens)
    t = []
    for i, token in enumerate(tokens):
        if split_pattern.search(token) is not None:
            corr_pattern = r'<choice(.*?)<corr>(.*?)</corr></choice>'
            matchobj = re.search(corr_pattern, token)
            to_corr = matchobj.group(2)
            text_res, changes, s_json = Processor.process_text(
                text=to_corr,
                show=True,
                delimiters=['<choice><reg>', '</reg><orig>', '</orig></choice>'],
                check_brackets=False
            )
            tokens[i] = f'<choice{matchobj.group(1)}<corr>{text_res}</corr></choice>'
        else:
            t = []
            for tok in token.split():
                if re.search(r'(>\[[0-9]*\])', tok):
                    t.append(tok)
                else:
                    text_res, changes, s_json = Processor.process_text(
                        text=tok,
                        show=True,
                        delimiters=['<choice><reg>', '</reg><orig>', '</orig></choice>'],
                        check_brackets=False
                    )
                    t.append(text_res)
            tokens[i] = " ".join(t)
    return ''.join(tokens)

def markup_choices_for_editorial_corrections(text):
    choice_pattern = re.compile(
        r'(<head.*?>[*, ]*)?(\s*(\w*?(\[([^0-9]*?)\])\w*)\s*)(?!\">)(</head>)?'
        # r'(<head[^>]*?>[*, ]*)?(\s*(\w*?(\[(.*?)])\w*)\s*)(?!\">)(</head>)?'
    )
    illegible_pattern = re.compile(  # решить, что с этим делать
        r'(\[\d+.*?не\s*разобр.*?\])|'  # [2 неразобр.]
        r'(\w+\[\w+\?\])|'  # вл[иянием?]
        r'(\[\?\])'  # [?]
    )
    crossed_out_pattern = re.compile(
        # r'(<.*?>)?(з|З)ач(е|ё)ркнуто:(<.*?>)?'
        r'(<[^>]*?>)?(з|З)ач(е|ё)ркнуто:(<[^>]*?>)?'
    )
    choice_result = re.findall(choice_pattern, text)

    for i in choice_result:
        if (
                i[0] or  # if inside head
                illegible_pattern.search(i[2]) is not None or
                crossed_out_pattern.search(i[2]) is not None
        ):
            continue
        sub_1 = re.sub(r'\[|\]', r'', i[2])
        sub_2 = re.sub(r'\[|\(', r'\\[', i[2])
        sub_3 = re.sub(r'\]|\)', r'\\]', sub_2)
        sub_4 = re.sub('\[.*?\]', '', i[2])
        choice_attribute = re.search('<.*?>(.*?)<.*?>', i[2])  # [<hi>хвастовство</hi>]
        if choice_attribute is None:
            choice_attribute = i[2]
        else:
            choice_attribute = choice_attribute.group(1)
        replacement = (f'<choice original_editorial_correction="{choice_attribute}">'
                       f'<sic>{sub_4}</sic><corr>{sub_1}</corr></choice>')
        reg_for_repl = f'(?<!="){sub_3}(?!">)'
        text = re.sub(reg_for_repl, replacement, text)
    return text

def shorten_text(text):
    text = re.sub("\n", "", text)
    return text

def  brasket_hyphenation(text):
    pattern = re.compile('(<.*?>)(.*\[[^\]]*)(<.*?>)(<.*?>)([^\[]*\])(<.*?>)')
    text = pattern.sub("\g<1>\g<2>\g<5>\g<6>", text)
    return text

def markup_edit_cycle(text):
    pattern = re.compile("([^0-9]*\[[^0-9]\])([^0-9]*\[[^0-9]\][^0-9]*)")
    words = []
    for word in text.split():
        result = pattern.search(word)
        if result:
            part = markup_choices_for_editorial_corrections(result.group(1))            
            words.append(part)   
            part = markup_choices_for_editorial_corrections(result.group(2))            
            words.append(part)   

        else:
            words.append(markup_choices_for_editorial_corrections(word))
    return " ".join(words)

def normalise_em(text):
    pattern1 = re.compile(r"(<em>)\[([^><]*)(</{0,1}em>){0,1}([^<>]*)(</{0,1}em>){0,1}([^<>]*)\](</em>)")
    pattern2 = re.compile(r"\[<em>([^><]*)\]([^><]*)</em>")

    pattern3 = re.compile(r"<em>([^><]*)\[([^><]*)</em>\]")
    pattern4 = re.compile(r"<em>([^><]*)</em><em>([^><]*)</em>") 
    pattern5 = re.compile("\[<em>([^><]+)</em>\]")
    pattern6 = re.compile("\[<em>([^><]+)</em><em>([^><]+)</em>\]")
    if pattern1.search(text):
        
        text = pattern1.sub("\g<1>[\g<2>\g<4>\g<6>]\g<7>", text)
    elif pattern2.search(text):
        text = pattern2.sub("<em>[\g<1>]\g<2></em>", text)
    if pattern3.search(text):
        text = pattern3.sub("<em>\g<1>[\g<2>]</em>", text)
    if pattern4.search(text):
        text = pattern4.sub("<em>\g<1>\g<2></em>", text)
    elif pattern5.search(text):
        text = pattern5.sub("<em>[\g<1>]</em>", text)
    elif pattern6.search(text):
        text = re.sub("<em>[\g<1>g<2>]</em>", text)

    return text 

def preprosess(str_tag):
    a = shorten_text(str(str_tag))
    a = normalise_em(a)
    a = markup_choices_for_editorial_corrections(a)
    a = markup_choices_for_prereform_spelling(a)
    a = del_tag(a)
    return a
def preprosess_exeption(str_tag):
    if re.search("<1 стерто\]", str_tag):
        a = re.sub("<1 стерто\]", "[1 стерто]", str_tag)
    a = normalise_em(str_tag)
    a = brasket_hyphenation(a)
    a = markup_edit_cycle(a)
    a = markup_choices_for_prereform_spelling(a)  
    return a
def html_to_xml(html_tag):
   html_tag = str(html_tag)
   preprosessed =  preprosess(html_tag)
   try:
       tag = etree.fromstring(preprosessed)
   except etree.XMLSyntaxError as err:
       preprosessed = preprosess_exeption(html_tag)
       tag = etree.fromstring(preprosessed)
   return tag

def fill_template(root):
    title = root.find(".//title")
    title.text = get_title(soup, file).text
    biblScope = root.find(".//biblScope")
    biblScope.text = str(vol_id)

def subsitute_notes(soup, p):
    for note in p.findall(".//a[@type='note']"):
        #print(note.text)
        #print("cvcvcvcvcvccv")
        note_number = note.get("href")[1::]
        number = note_number[1::]
        back_note = soup.find(id=note_number)
        back_note_text = shorten_text(back_note.find("p").get_text())
        note.text = back_note_text
        note.tag = "note"
        for atr in note.keys():
            del note.attrib[atr]
        note.set("{" + ns["xi"] + "}" + "id", f"note{number}")
    return p
def get_date2(text):
    pattern = re.compile("(\[)*.*[0-9]+.*(\])*")
    year_pattern = re.compile("1[0-9]{3}")
    month_pattern2 = re.compile(".*(январ.{0,1}|феврал.{0,1}|апрел.{0,1}|март.{0,1}|ма.{0,1}|июн.{0,1}|июл.{0,1}|август.{0,1}|сентябр.{0,1}|октябр.{0,1}|ноябр.{0,2}|декабр.{0,1}|iюн.{0,1}|iюл.{0,1})\s*([0-9]{0,2})")

    if isinstance(text, str):
        text = re.sub("І", "I", text)
        text, changes, s_json = Processor.process_text(
                text=text,
                show=False,
                delimiters=False,
                check_brackets=False
            ) 
        text = re.sub("Окт", "Октября", text)
        text = re.sub("(Авг|Ав)", "Августа", text)
        text = re.sub("Апр", "Апреля", text)
        text = re.sub("Дек", "Декабря", text)

        words = text.lower().split()
        l = []
        for word in words:
            if re.search("\d+", word) or month_pattern2.search(word):
                l.append(word)
            text = (" ".join(l))

        if year_pattern.search(text):
                date = get_date(text)
               # print(date, text, 1)
                return date, text
        elif month_pattern2.search(text):
            date = get_date(f"{date2parser} {text}")
            #print(date, f"{date2parser} {text}", 2)
            #print(f"{date2parser} {text}")
            return date, text
        else:
           
            print(text, 3)
            #print(f"{date2parser} {text}")
            return None
    else:
       # print(text, 4)
        return None

def entry_line_tag(tag_, text_tag):
    patterns = (re.compile("1[0-9]{3}—1[0-9]{3}\s*\?\s*гг"), 
                re.compile("1[0-9]{3}\s*\?\s*г"))
    global date2parser 
    if tag_.tag == "p":
        #print(etree.tostring(tag_, encoding="unicode"))
        text = ''.join(tag_.itertext())
        date = None
        for em in tag_.findall("./em"):
            if get_date2(em.text) is not None:
                d, date_text = get_date2(em.text)
            else:
                d = None

            if d is not None:
                date = d
        if date is None:
            text_tag.append(subsitute_notes(soup, tag_))
        else:
             div = etree.Element("div")
             div.set("type", "entry")
             datetag = etree.Element("date")
             div.append(datetag)
             div.append(subsitute_notes(soup, tag_))
             #print(tag_.text)
             if date[0] == "Not_B_A":
                 datetag.set("notBefore", date[1]["notBefore"])
                 datetag.set("notAfter", date[1]["notAfter"])
             elif date[0] == "date_when":
                 datetag.set("when", date[1]["when"])
             elif date[0] == "Not_B_A_when":
                 datetag.set("notBefore", date[1]["notBefore"])
                 datetag.set("notAfter", date[1]["notAfter"])
                 datetag.set("when", date[1]["when"])

             datetag.text = date_text


             text_tag.append(div)
    else:
        text_tag.append(subsitute_notes(soup, tag_))
        if "h" in tag_.tag:
            for pattern1 in patterns:
                if isinstance(tag_.text, str):
                    if pattern1.search(tag_.text):
                        date2parser = pattern1.search(tag_.text).group()


def make_file(file):        
    root = TEI_template()
    text_tag = etree.Element("text")
    root.append(text_tag)
    pattern_one_div = '''<p class="left">Январь. 1 \[14\]\. Вторникъ'''
    print(get_title(soup, file))
    fill_template(root)
    for part in html_dict[file]:
        for child in id_to_html(soup, part):
            if isinstance(child, bs4.element.Tag):
                if re.search(pattern_one_div, shorten_text(str(child))):
                    for child_div in child:
                        if isinstance(child_div, bs4.element.Tag):
                            tag = html_to_xml(child_div)
                            
                            entry_line_tag(tag, text_tag)
                        
                                
                else:
                            
                    tag = html_to_xml(child)
                    entry_line_tag(tag, text_tag)
    return root

def change2tei(root):
    name_space = "http://www.tei-c.org/ns/1.0"
    text = root.find(f".//text")
    for tag_ in text.iter():
        a = tag_.tag
        if a in tag_dict:
            atrib2 = tag_.items()
            #print(atrib2)
            tag_.tag = tag_dict[a]
            for atr in atrib2:
                if atr[0] in atr_dict:
                    tag_.set(atr_dict[atr[0]], atr[1])
                    del tag_.attrib[atr[0]]
                    if tag_.tag == "hi":
                        tag_.set("style", atr[1])
                        del tag_.attrib["rend"]
        elif tag_.tag == "a" and "name" in tag_.keys():
            atr = tag_.get("name")
            tag_.tag = "pb"
        elif tag_.tag == "img":
             link = tag_.get("src")
             file_name = link.split("/")[-1]
             name_img = f"vol{vol_id}_{file_name}"
             image = get_img(link)
             with open(name_img, "wb") as f:
                 f.write(image)
             atrib2 = tag_.items()
             for atr in atrib2:
                 del tag_.attrib[atr[0]]
            
             tag_.tag = "graphic"
             tag_.set("url", f"TEI/images/{name_img}")
                #else:
                  #  tag_.set(atr[0], atr[1])

                



def get_date(text):
    bibl_pattern = "(Датируется|Впервые опубликовано|Автограф|Год в дате|На копии письма помечено|Печатается по|опубликовано| опубликовано в|Написано рукой|Написано на обороте|Публикуемый отрывок|Приписка к письму|абзац вписан|Ответ на письмо Страхова|Год устанавливается|Публикуемый отрывок|Написано на гранке|Личность адресата|по рукописной копии)"
    choice_pattern = "\s*([А-Яа-я]*?(\[(.*?)\])[А-Яа-я]*)\s*"
    choice_pattern2 = "\s*([А-Яа-я]*?(\[(.*?)\])[А-Яа-я]*?)\s*"
    data1 = "1862? г. Июля 1."
    data2 = "1864 г."
    data3 = "1856—1859 гг."
    data4 = "1874 г. февраль — март, до 15. я. п."
    data5  = "1840 г. июля 20."
    date_pattern1 = "(1[0-9]{3})\s*\?*\s*(-|—)\s*(1[0-9]{3})\s*\?*\s*гг.{0,2}$"
    date_pattern2 = "—"
    date_pattern3 = "(начало|середина|конец|первая половина|)"
    date_pattern4 = "до\s*[1-90]{1,2}"
    place_pattern =  "\s*(я. п.|москва|петербург|козлова засека.|бегичевка.|гриневка)"
    date_pattern5 = "(1[1-90]{3}) или (1[1-90]{3}) г.*"
    date_pattern6 = "^(1[1-90]{3})-е гг."
    date_pattern7 = "^(1[1-90]{3})\?* г."
    date_pattern8 = "(1[1-90]{3})—(1[1-90]{3})-е\s*.*\s*.(начало|середина|конец|первая половина|вторая половина).+"
    date_pattern9 = "(1[1-90]{3})—(1[1-90]{3})-е гг."
    part_pattern = ",*\s*(начало|середина|конец|первая половина|вторая половина).{0,2}$"
    part_pattern2 = ".*\s*(начало|середина|конец|первая половина|вторая половина).{0,2}"
    month_parts_dic = {"начало": ["01 01", "04 30"], "середина" : ["05 01", "08 31"], "конец": ["09 01", "12 31"], "первая половина":["01 01", "05 31"], "вторая половина":["06 01", "12 31"]}
    month_pattern = ".*(январ.{0,2}|феврал.{0,2}|апрел.{0,}|март.{0,2}|ма.{0,2}|июн.{0,2}|июл.{0,2}|август.{0,2}|сентябр.{0,2}|октябр.{0,2}|ноябр.{0,2}|декабр.{0,2}|iюн.{0,1}|iюл.{0,1})\s([0-9]{0,2})"
    month_pattern2 = ".*(январ.{0,1}|феврал.{0,1}|апрел.{0,1}|март.{0,1}|ма.{0,1}|июн.{0,1}|июл.{0,1}|август.{0,1}|сентябр.{0,1}|октябр.{0,1}|ноябр.{0,2}|декабр.{0,1}|iюн.{0,1}|iюл.{0,1})\s*([0-9]{0,2})"
    month_pattern3 = ".*(январ.{0,2}|феврал.{0,2}|апрел.{0,}|март.{0,2}|ма.{0,2}|июн.{0,2}|июл.{0,2}|август.{0,2}|сентябр.{0,2}|октябр.{0,2}|ноябр.{0,2}|декабр.{0,2}|iюн.{0,1}|iюл.{0,1})\s*([0-9]{1,2})\s*—\s*([0-9]{1,2})"
    year_part_dic = {"начало": [0, 4], "середина":[4, 7], "конец": [7, 9]}
    day_part_dic = {"начало": ["01", "10"], "середина" : ["11", "20"], "первая половина":["01", "15"]}
    season_dic = {"лето":["06 01"]}
    date_pattern10 = "((1[1-90]{3}).?\sг.)\s*" + month_pattern2 + "\s*.*\s*после\s*([1-90]{1,2})"
    date_pattern11 = "((1[1-90]{3}).?\sг.)\s*" + month_pattern2 + "\s*—\s*" + month_pattern2 + "\s*.*\s*до\s*([1-90]{1,2})"
    date_pattern12 = "((1[1-90]{3}).?\sг.).*" + part_pattern2 + "\s—\s((1[1-90]{3}).?\sг.)." + part_pattern2
    spes_date_pattern = "1896\? г., 1904\? г. сентябрь или 1905\? г. январь."
    result = re.search("(1[0-9]{3})\sг\.," + part_pattern2 + "\s*—\s*(1[0-9]{0,3})\sг.",  "1901 г., конец — 1902 г.")    

    a = re.sub(place_pattern,r"",text.lower())
    
    if re.search(date_pattern1, a):                   
        result = re.search(date_pattern1, a)
        date_from = result.group(1) + " 01 01"
        date_to = result.group(3) + " 12 31"
        date_from = dateparser.parse(date_from, languages = ["ru"])
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]
    elif re.search("1893 г., до июля.", a):
        date_from = "1893-01-01"
        date_to = "1893-06-30"
        date_final = ["Not_B_A", {"notBefore":"1893-01-01", "notAfter": "1893-06-30"}]
    
    elif re.search("1885 г. Конец ноября — первые числа декабря.", text):
        date_from = "1885-11-21"
        date_to = "1885-12-10"
        date_final = ["Not_B_A", {"notBefore":date_from, "notAfter": date_to}]
    
    elif re.search("1894 г. Апреля 28 — 80", text):
        date_from = "1894-04-28"
        date_to = "1894-04-30"
        date_final = ["Not_B_A", {"notBefore":date_from, "notAfter": date_to}]

    elif re.search("1894 г Конец мая, после 23-го.", text):
        date_from = "1894-05-23"
        date_to = "1894-05-31"
        date_final = ["Not_B_A", {"notBefore":date_from, "notAfter": date_to}]

    elif re.search("1895 г. Конец июля, не позже 30-го.", text):
        date_from = "1895-07-21"
        date_to = "1895-07-30"
        date_final = ["Not_B_A", {"notBefore":date_from, "notAfter": date_to}]

    elif re.search("1870-е\? гг. сентября 13.", a):
        date_when = "-10-13"
        date_from = "1871-09-13"
        date_to = "1880-09-13"
        date_final = ["Not_B_A_when", {"notBefore":date_from, "notAfter": date_to, "when":date_when}]

    elif re.search("1868 г. август  — 1870 г. ноябрь.", a):
        date_final = ["Not_B_A", {"notBefore":"1868-08-01", "notAfter":"1870-11-30"}]

    elif re.search("1892 г. апрель, около 20.", a):
        date_from = "1892-03-15"
        date_to = "1892-03-25"
        date_final = ["Not_B_A", {"notBefore":"1892-03-15", "notAfter": "1892-03-25"}]

    elif re.search(date_pattern6 + "\sлето$", a):
        result = re.search(date_pattern6 + "\sлето$")
        date_from = result.group(1) + " 06 01"
        date_to = str(int(result.group(1) + 10)) + " 08 31" 
        date_from = dateparser.parse(date_from, languages = ["ru"])
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

    elif re.search("1890 г. — 1891 г., октябрь, до 26.", a):
        date_from = "1890-10-01"
        date_to = "1891-10-26"
        date_final = ["Not_B_A", {"notBefore":"1890-10-01", "notAfter": "1891-10-26"}]

    elif re.search(date_pattern6 + part_pattern[:-1] + "\s*—\s*(1[0-9]{3})-е\s*гг.$" , a):
          result = re.search(date_pattern6 + part_pattern[:-1] + "\s*—\s*(1[0-9]{3})-е\s*гг.$" ,  a)
          date_from = str(int(result.group(1)) +  year_part_dic[result.group(2)][0]) + " 01 01"
          date_to = str(int(result.group(3)) + 10)  + " 12 31"
          date_from = dateparser.parse(date_from, languages = ["ru"])
          date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
          date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

    elif re.search("1888\? г. ноябрь — 1889 г. апрель..", a):
        date_from = "1888-11-01"
        date_to = "1889-04-30"
        date_final = ["Not_B_A", {"notBefore":date_from, "notAfter": date_to}]

    elif re.search("(1[0-9]{3})\s*г\.\?*\s*(-|—)\s*(1[0-9]{3})\sг\.\s*" + part_pattern2,  a):
        result = re.search("(1[0-9]{3})\s*г\.\?*\s*(-|—)\s*(1[0-9]{3})\sг\.\s*" + part_pattern2,  a)
        date_from = result.group(1) + " " + " 01 01"
        date_to = result.group(3) + " " + month_parts_dic[result.group(4)][1]
        date_from = dateparser.parse(date_from, languages = ["ru"])
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

          
    elif re.search("1900 г. октябрь, после 13—1901 г., апрель.", a):
        date_from = "1900-10-13"
        date_to = "1901-03-01"
        date_final = ["Not_B_A", {"notBefore":date_from, "notAfter": date_to}]

    elif re.search(date_pattern7 + month_pattern2 + ",\sдо\s([0-9]{1,2})" ,  a):
        result = re.search(date_pattern7 + month_pattern2 + ",\sдо\s([0-9]{1,2})" ,  a)
        date_from = result.group(1) + " " + result.group(2) + "01"
        date_to =  result.group(1) + " " + result.group(2) + " " + result.group(4)
        date_from = dateparser.parse(date_from, languages = ["ru"])
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

    elif re.search(date_pattern1[:-1] + ", лето",a):

        result = re.search(date_pattern1[:-1] + ", лето", a)
        date_from = result.group(1) + " 06 01"
        date_to = result.group(3) + " 08 31"
        date_from = dateparser.parse(date_from, languages = ["ru"])
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

    elif re.search(date_pattern1[:-1] + month_pattern2,a):
        result = re.search(date_pattern1[:-1] + month_pattern2,a)    
        date_from = result.group(1) + " " + result.group(4) + " " + result.group(5)
        date_to = result.group(3) + " " + result.group(4) + " " + result.group(5)
        date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'})

        if result.group(5):
            date_when = "-" + result.group(4) + " " + result.group(5)
        else: 
            date_when = "-" + result.group(4) + " " + "-"
        date_when = dateparser.parse(date_when, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A_when", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d"), "when":date_when.strftime("-%m-%d")}] if (date_from is not None and date_from is not None) else None

        
    elif re.search("(1[0-9]{3}) г\., лето.", a):
        result = re.search("(1[0-9]{3}) г\., лето.", a)
        date_from = result.group(1) + " 06 01"
        date_to = result.group(1) + " 08 31"
        date_from = dateparser.parse(date_from, languages = ["ru"])
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

    elif re.search("1874 г\. февраль — март, до 15\.", a):
        date_from = "1874-02-01"
        date_to = "1874-03-15"
        date_final = ["Not_B_A", {"notBefore":date_from, "notAfter": date_to}]

    elif re.search(spes_date_pattern, a):
        date_when = ["1896-09-", "1904-09-", "1905-01-"]
        date_final = ["Not_B_A", {"notBefore":"1896-09-01", "notAfter": "1905-01-31"}]

    elif re.search(date_pattern10, a):
        result = re.search(date_pattern10, a)
       # print("sss")
        date_from = result.group(1) + " " + result.group(3) + " " + result.group(5) 
        date_to = result.group(1) + " " + result.group(3)
        date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last',  'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

    elif re.search(date_pattern11, a):
        print(date_pattern11)
        result = re.search(date_pattern11, a)
        date_from = result.group(1) + " " + result.group(3) 
        # exp 
        date_to = result.group(1) + " " + result.group(5) + " " + result.group(7)
        date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last',  'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

    elif re.search(date_pattern12, a):
        print("111")
        result = re.search(date_pattern12, a)
        date_from = result.group(1) + " " + month_parts_dic[result.group(3)][0] 
        date_to = result.group(4) + " " + month_parts_dic[result.group(6)][1] 
        date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last',  'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

    elif re.search(date_pattern5, a):
        result = re.search(date_pattern5, a)
        date_from = result.group(1)
        date_to = result.group(2) 
        if re.search(month_pattern, a):
            result2 = re.search(month_pattern, a)
            date_from = date_from + " " + result2.group(1)
            date_to = date_to + " " + result2.group(1)
            if result2.group(2):
                date_from = date_from + " " + result2.group(2)
                date_to = date_to + " " + result2.group(2)
        else: 
            date_from = date_from + " " + "01 01"
            date_to = date_to + " " + "12 31"
        date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        #print(dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'}), dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'}))
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]


    elif re.search(date_pattern6, a):
        result = re.search(date_pattern6, a)
        date_from = str(int(result.group(1)))   
        date_to = str(int(result.group(1))) 
        if re.search(part_pattern, a):
            result2 = re.search(part_pattern, a)
            if result2.group(1) in year_part_dic:
                date_from = str(int(date_from) +  year_part_dic[result2.group(1)][0])
                date_to = str(int(date_to) + year_part_dic[result2.group(1)][1])
            
            else:
                date_from = str(int(result.group(1)))   
        
                date_to = str(int(result.group(1)) +9) 
        else:
            date_from = str(int(result.group(1)))   
            date_to = str(int(result.group(1)) + 9)      
        date_from = date_from + " " + "01 01"
        date_to = date_to + " " + "12 31"    


        date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first',  'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

    elif re.search(date_pattern7, a):
        #  print("date_pattern7")
          result = re.search(date_pattern7, a)
          if re.search("(1[0-9]{3})\sг\.," + part_pattern2 + "\s*—\s*[0-9]{0,3}\sг.$", a):
              result = re.search("(1[0-9]{3})\sг\.," + part_pattern2 + "\s*—\s*[0-9]{0,3}\sг.", a)
              date_from = result.group(1) + month_parts_dic[0] 
              date_to = result.group(3) + ' 12 31'
              date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
              date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'})
              date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

          elif re.search(month_pattern2 + "\s*—\s*" + month_pattern2, a):
              print("11")
              spes_result = re.search(month_pattern2 + "\s*—\s*" + month_pattern2, a)
              date_from = result.group(1) + " " + spes_result.group(1) + " " + spes_result.group(2)
              date_to = result.group(1) + " " + spes_result.group(3) + " " + spes_result.group(4)
              date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
              date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'})
              date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]
           
          elif re.search(month_pattern2 + "\s*-\s*" + month_pattern2, a):
              print("11")
              spes_result = re.search(month_pattern2 + "\s*-\s*" + month_pattern2, a)
              date_from = result.group(1) + " " + spes_result.group(1) + " " + spes_result.group(2)
              date_to = result.group(1) + " " + spes_result.group(3) + " " + spes_result.group(4)
              date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
              date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'})
              date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

          elif re.search(month_pattern2, a):
              result2 = re.search(month_pattern2, a)
              if result2.group(2):
                 # print('sss')
                  if re.search(month_pattern2 + "\?*\s*(-|—)\s*([0-9]{1,2})\?*", a):
                      result3 = re.search(month_pattern2 + "\?*\s*(-|—)\s*([0-9]{1,2})\?*", a)
                      date_from = result.group(1) + " " + result3.group(1) + " " + result3.group(2)
                      date_to = result.group(1) + " " + result3.group(1) + " " + result3.group(4)
                      date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
                      date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'})
                      date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]
                  elif re.search(month_pattern3, a):

                      result3 = re.search(month_pattern3, a)
                      date_from = result.group(1) + " " + result2.group(1) + " " + result3.group(2)
                      date_to = result.group(1) + " " + result2.group(1) + " " + result3.group(3)
                      date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
                      date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'})
                      date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}] if date_from and date_to is not None else None
                  else:
                      date_when = dateparser.parse(a, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
                      #date_final = ["date_when", {"when":date_when.strftime("%Y-%m-%d")}]
                      date_final = ["date_when", {"when":date_when.strftime("%Y-%m-%d")}] if date_when is not None else None

                      #print(dateparser.parse(a, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'}))
              elif re.search(part_pattern2 + month_pattern2, a):
                  result4 = re.search(part_pattern2 + month_pattern2, a)
                  #if re.search(part_pattern2 + month_pattern2 + "\s*—\s*" + month_pattern2, a):
                   #   result4 = re.search(part_pattern2 + month_pattern2 + "\s*—\s*" + month_pattern2, a):
                    #  month_1 
                  if result4.group(1) == "конец":
                      date_from = result.group(1) + " " + result4.group(2) + " " + "21"
                      date_to = result.group(1) + " " + result4.group(2)
                      date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'})
                      date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
                  elif result4.group(1) == "вторая половина":
                      date_from = result.group(1) + " " + result4.group(2) + " " + "16"
                      date_to = result.group(1) + " " + result4.group(2)
                      date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'})
                      date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
                  else:
                      date_from = result.group(1) + " " + result4.group(2) + " " + day_part_dic[result4.group(1)][0]
                      date_to = result.group(1) + " " + result4.group(2) + " " + day_part_dic[result4.group(1)][1]
                      date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'})
                      date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
                  date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}] if date_from and date_to is not None else None

              elif re.search(part_pattern, a):

                  result3 = re.search(part_pattern, a)
                  if result3.group(1) == "конец":
                      date_from = result.group(1) + " " + result2.group(1) + " " + "21"
                      date_to = result.group(1) + " " + result2.group(1)
                      date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
                      date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'})
                      #print(dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'}),dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'}) )
                      date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

                  elif result3.group(1) == "вторая половина":
                      date_from = result.group(1) + " " + result2.group(1) + " " + "16"
                      date_to = result.group(1) + " " + result2.group(1)
                      date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
                      date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'}) 
                      date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

                      #print(dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'}),dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'}) )    
                  else:
                      date_from = result.group(1) + " " + result2.group(1) + " " + day_part_dic[result3.group(1)][0]
                      date_to = result.group(1) + " " + result2.group(1) + " " + day_part_dic[result3.group(1)][1]
                      date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
                      date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'}) 
                      date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]
                      #print(dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'}),dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'}) )    

              
              else:
                 # print("ssss")
                  date_from = dateparser.parse(a, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
                  date_to = dateparser.parse(a, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'last', 'DATE_ORDER': 'YMD'})
                  #date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]
                  date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}] if date_from is not None else None

          elif re.search(part_pattern, a):
              result2 = re.search(part_pattern, a)
              date_from = result.group(1) + " "  + month_parts_dic[result2.group(1)][0]
              date_to = result.group(1) + " "  + month_parts_dic[result2.group(1)][1]
              date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
              date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first',  'DATE_ORDER': 'YMD'})
              date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

          else:
              date_from = result.group(1) + " " + " 01 01"
              date_to = result.group(1) + " " + " 12 31"   
              date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
              date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first',  'DATE_ORDER': 'YMD'})
              date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]



    elif re.search(date_pattern8, a):
        result = re.search(date_pattern8, a)
        date_from = result.group(1) + " " + "01 01"
        date_to = str(int(result.group(2)) + year_part_dic[result.group(3)][1]) + " " + "12 31"
        date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first',  'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

        #print(dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'}), dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first',  'DATE_ORDER': 'YMD'}))

    elif re.search(date_pattern9, a):
        result = re.search(date_pattern9, a)
        date_from = result.group(1) + " " + "01 01"
        date_to = str(int(result.group(2)) + 9) + " " + "12 31"
        date_from = dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        date_to = dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first',  'DATE_ORDER': 'YMD'})
        date_final = ["Not_B_A", {"notBefore":date_from.strftime("%Y-%m-%d"), "notAfter": date_to.strftime("%Y-%m-%d")}]

        #print(dateparser.parse(date_from, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'}), dateparser.parse(date_to, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first',  'DATE_ORDER': 'YMD'}))
        #print("I AM HEREE")
    
    else: 
        #print(dateparser.parse(a, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'}))
        date_when = dateparser.parse(a, languages = ["ru"], settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
            
        date_final = ["date_when", {"when":date_when.strftime("%Y-%m-%d")}] if date_when is not None else None
    return date_final           

def pipline():
    global html_dict
    global vol_id
    global file
    global soup
    global url 
    for vol_id in volume_id:
      url =  f"http://tolstoy.ru/online/90/{vol_id}/"
      html_text = get_html(url)
      soup = BeautifulSoup(html_text, 'html.parser')
      first_id, last_id = volume_id[vol_id][0], volume_id[vol_id][1]

      html_dict = get_html_dict(soup, first_id, last_id)
      print(vol_id)
      for file in html_dict:
          file2 = make_file(file)
          change2tei(file2)
          #print("new")
          print(etree.tostring(file2, pretty_print=True, encoding = "unicode"))
