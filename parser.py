import urllib.request
import bs4
from bs4 import BeautifulSoup
import requests
import re
from lxml import etree
from prereform2modern import Processor


volume_id = {47:["h000011001", "h000011002"], 48:["h000011001", "h000011013"],
             49:["h000010001", "h000010005"], 50:["h000010001", "h000010003"],
             51:["h000008001","h000008004"], 52:["h000008001", "h000008006"],
             53:["h000010001","h000010005"], 54:["h000011001", "h000011009"],
             55:["h000011001","h000011009"], 56:["h000010001", "h000010009"],
             57:["h000011001", "h000011003"], 58:["h000012001", "h000012014"]}

def get_html(url):
    html = requests.get(url).text
    return html 
  
def TEI_template():
    """ 
    Function creates TEI (XML) template for Tolstoy's notebooks
    :param: None
    :return: lxml.etree._Element
    """
    ns = {None:"http://www.tei-c.org/ns/1.0", "xi": "http://www.w3.org/2001/XInclude"}
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
    text = etree.Element("text")
    root.append(text)
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
            text_res, changes, s_json = Processor.process_text(
                text=token,
                show=True,
                delimiters=['<choice><reg>', '</reg><orig>', '</orig></choice>'],
                check_brackets=False
            )
            tokens[i] = text_res
            # print(tokens)
    return ''.join(tokens)

def markup_choices_for_editorial_corrections(text):
    choice_pattern = re.compile(
        r'(<head.*?>[*, ]*)?(\s*(\w*?(\[([^0-9]*?)])\w*)\s*)(?!\">)(</head>)?'
        # r'(<head[^>]*?>[*, ]*)?(\s*(\w*?(\[(.*?)])\w*)\s*)(?!\">)(</head>)?'
    )
    illegible_pattern = re.compile(  # решить, что с этим делать
        r'(\[\d+.*?не\s*разобр.*?])|'  # [2 неразобр.]
        r'(\w+\[\w+\?])|'  # вл[иянием?]
        r'(\[\?])'  # [?]
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
        sub_1 = re.sub(r'\[|]', r'', i[2])
        sub_2 = re.sub(r'\[', r'\\[', i[2])
        sub_3 = re.sub(r']', r'\\]', sub_2)
        sub_4 = re.sub('\[.*?]', '', i[2])
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
