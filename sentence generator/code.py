'''
Код генерирует случайные предложения, используя текстовые файлы со словами
'''

import random

def rand_vervb(verbs):
    ''' Эта функция возращает случайный глагол в личной
    форме, ее аргумент текстовый файл'''
    with open(verbs,encoding = "utf-8-sig") as f:
        v = f.read().split()
        r_verb = random.choice(v)
    return r_verb

def rand_adverb(adverbs):
    ''' Эта функция возращает случайное наречие,
    ее аргумент текстовый файл'''
    with open(adverbs,encoding = "utf-8-sig") as f:
        a = f.read().split()
        r_adverb = random.choice(a)
    return r_adverb

def rand_subject(nouns):
    ''' Эта функция возращает случайное подлежащие,
    ее аргумент текстовый файл'''
    with open(nouns,encoding = "utf-8-sig") as f:
        s = f.read().split()
        r_subject = random.choice(s)
    return r_subject

def rand_object(objects):
    ''' Эта функция возращает случайное дополнение,
    ее аргумент текстовый файл'''
    with open(objects,encoding = "utf-8-sig") as f:
        o = f.read().split() 
        r_object = random.choice(o)   
    return r_object

def rand_imper(imperatives, encoding = "utf-8-sig"):
    ''' Эта функция возращает случайный глагл в императиве 
    или инфинитиве,ее аргумент текстовый файл'''
    with open(imperatives) as f:
        i = f.read().split()
        r_imper = random.choice(i)
        if r_imper.endswith("ть"):
            r_imper = "Давай" + " " + r_imper 
    return r_imper             

def sentence(nouns,adverbs,verbs,objects,imperatives):
    ''' Это функция возращает мн. из 5 случайных предл.,
    ее аргументы 5 текстовых файлов'''
    a_sent = rand_subject(nouns) + " " + rand_adverb(adverbs) + " " +\
    rand_vervb(verbs) + " " + rand_object(objects) + "."
    q_sent = rand_subject(nouns) + " " + "ли" + " " + rand_adverb(adverbs) + " " +\
    rand_vervb(verbs) + " " + rand_object(objects) + "?"
    n_sent = rand_subject(nouns) + " " + "не" + " " +\
    rand_vervb(verbs) + " " + rand_object(objects) + "."
    c_sent = "Если" + " " + rand_subject(nouns).lower() + " " + rand_adverb(adverbs) + " " +\
    rand_vervb(verbs) + " " + rand_object(objects) + "," + " " + "то" + " " +\
    rand_subject(nouns).lower() + " " + rand_adverb(adverbs) + " " +\
    rand_vervb(verbs) + " " + rand_object(objects) +"."
    i_sent = rand_imper(imperatives) + " " + rand_object(objects) + "!"
    return set([a_sent,q_sent,n_sent,c_sent,i_sent])
    
def main():
    text = sentence("nouns.txt","adverbs.txt","verbs.txt","objects.txt","imperatives.txt")
    for s in text:
        print(s)


if __name__ == '__main__':
    main()
