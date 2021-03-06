import urllib.request
import bs4
from bs4 import BeautifulSoup
import requests
import re
from prereform2modern import Processor
from lxml import etree


ns = {None:"http://www.tei-c.org/ns/1.0", "xi": "http://www.w3.org/2001/XInclude"}

volume_id = {47:["h000011001", "h000011002"], 48:["h000011001", "h000011013"],
             49:["h000010001", "h000010005"], 50:["h000010001", "h000010003"],
             51:["h000008001","h000008004"], 52:["h000008001", "h000008006"],
             53:["h000010001","h000010005"], 54:["h000011001", "h000011009"],
             55:["h000011001","h000011009"], 56:["h000010001", "h000010009"],
             57:["h000011001", "h000011003"], 58:["h000012001", "h000012014"]}

tag_dict = {"h2":"head", "h3":"head", "tr":"row", "td":"cell", "em":"hi"}

def get_html(url):
    html = requests.get(url).text
    return html 
  
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

    if pattern1.search(text):
        
        text = pattern1.sub("\g<1>[\g<2>\g<4>\g<6>]\g<7>", text)
    elif pattern2.search(text):
        text = pattern2.sub("<em>[\g<1>]\g<2></em>", text)
    if pattern3.search(text):
        text = pattern3.sub("<em>\g<1>[\g<2>]</em>", text)
    if pattern4:
        text = pattern4.sub("<em>\g<1>\g<2></em>", text)

    return text

def preprosess(str_tag):
    a = shorten_text(str(str_tag))
    a = normalise_em(a)
    a = markup_choices_for_editorial_corrections(a)
    a = markup_choices_for_prereform_spelling(a)
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

def entry_line_tag(tag_, text_tag):
    if tag_.tag == "p":
        #print(etree.tostring(tag_, encoding="unicode"))
        text = ''.join(tag_.itertext())
        if re.search("^(—|=)*$", text):
            text_tag.append(tag_)
        else:
             div = etree.Element("div")
             div.set("type", "entry")
             div.append(subsitute_notes(soup, tag_))
             text_tag.append(div)
    else:
        text_tag.append(subsitute_notes(soup, tag_))



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
            tag_.tag = tag_dict[a]


def pipline():
    global html_dict
    global vol_id
    global file
    global soup
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
          print(etree.tostring(file2, pretty_print=True, encoding = "unicode"))
#
