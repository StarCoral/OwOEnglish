#!/usr/bin/env python
# coding: utf-8

import math
import json
from collections import Counter 
from nltk import pos_tag, corpus
from nltk.corpus import wordnet, stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.data import load

from bs4 import BeautifulSoup
import requests


# import nltk
# nltk.download('tagsets')

lemmatizer = WordNetLemmatizer()
english_vocab = set(w.lower() for w in corpus.words.words())
tagdict = load('help/tagsets/upenn_tagset.pickle')

with open('query/etym.entries.v1.format.json') as f:
    data = json.load(f)

wordset = []
for word in data['results']:
    wordset.extend(word['foreigns'])
    wordset.extend(word['cross-references'])


pre_wordset = []
aff_wordset = []
suf_wordset = []

for word in wordset:
    if len(word) == 0 or word[0] == '*' or (word[0] == '-' and word[-1] == '-'):
        continue
    else:
        if word[0] == '-':
            suf_wordset.append(word[1:])
        elif word[-1] == '-':
            pre_wordset.append(word[:-1])
        else:
            aff_wordset.append(word)

pre_counter = Counter(pre_wordset)
aff_counter = Counter(aff_wordset)
suf_counter = Counter(suf_wordset)

pre_total = sum(pre_counter.values())
aff_total = sum(aff_counter.values())
suf_total = sum(suf_counter.values())


def segment(word):
    l = len(word)
    arr = []
    for i in range(1,l):
        for j in range(i, l):
            arr.append( (word[:i], word[i:j], word[j:]) )
    return arr


def seg_p(pre, aff, suf):
    if pre in pre_counter:
        p1 = pre_counter[pre]/pre_total
    else:
        p1 = 1 / (pre_total * (10**(len(pre))) )
    
    if aff in aff_counter:
        p2 = aff_counter[aff]/aff_total
    else:
        p2 = 1 / (aff_total * (10**(len(aff))) )
        
    if suf in suf_counter:
        p3 = suf_counter[suf]/suf_total
    else:
        p3 = 1 / (suf_total * (10**(len(suf))) )
        
    if aff == '':
        return (math.log10(p1) + math.log10(p3))
    else:
        return (math.log10(p1) + math.log10(p2) + math.log10(p3) )


def get_pos(word):
    return pos_dict[word]

def get_short_pos(word):
    pos = get_pos(word)
    #print(pos)
    if pos.startswith('N'):
        return wordnet.NOUN
    if pos.startswith('V'):
        return wordnet.VERB
    if pos.startswith('J'):
        return wordnet.ADJ
    if pos.startswith('R'):
        return wordnet.ADV
    
def get_origin(word):
    pos = get_short_pos(word)
    return lemmatizer.lemmatize(word, pos)

def word_p_2(word, recursive=False):
    #print(word)
    if len(word) < 6 and not recursive:
        return [word]
    if word == '':
        return 
    if (word in english_vocab) and ( len(word) <= 10 ) or len(word) <= 8:
        return [word]
    word_ss = segment(word)
    word_s_p = []
    for word_s in word_ss:
        word_s_p.append( (word_s, round(seg_p(word_s[0], word_s[1], word_s[2]), 3 ) ) )
    word_s_p = sorted( word_s_p, key=lambda x: x[1] , reverse=True)[0][0]
    print(word_s_p)
    temp = [word_p_2(token,True) for token in word_s_p]
    word_segment = []
    for _ in temp:
        if _ is not None:
            word_segment.extend(_)
    return word_segment

def seg_in_dict(word):
    if len(word) <= 8:
        return [word]
    word_ss = segment(word)
    word_s_p = []
    for word_s in word_ss:
        word_s_p.append( (word_s, round(seg_p(word_s[0], word_s[1], word_s[2]), 3 ) ) )
    word_s_p = sorted( word_s_p, key=lambda x: x[1] , reverse=True)[0][0]
    temp = [ get_segment(token) for token in word_s_p]
    temp = [word_p_2(token,True) for token in word_s_p]
    word_segment = []
    for _ in temp:
        if _ is not None:
            word_segment.extend(_)
    return word_segment

def seg_not_in_dict(word):
    if word == '':
        return None
    if len(word) <= 8:
        return [word]
    word_ss = segment(word)
    word_s_p = []
    for word_s in word_ss:
        word_s_p.append( (word_s, round(seg_p(word_s[0], word_s[1], word_s[2]), 3 ) ) )
    word_s_p = sorted( word_s_p, key=lambda x: x[1] , reverse=True)[0][0]
    temp = [ get_segment(token) for token in word_s_p]
    word_segment = []
    for _ in temp:
        if _ is not None:
            word_segment.extend(_)
    return word_segment

def get_segment(word):
    if word in english_vocab:
        return seg_in_dict(word)
    else:
        return seg_not_in_dict(word)

def get_verb_segment(word):
    pos = get_pos(word)
    ori = get_origin(word)
    if pos == 'VBD':
        return [ori, "ed"]
    elif pos == 'VBG':
        return [ori, "ing"]
    else:
        return get_segment(word)



def get_bs_object(word):
    url = "https://dictionary.cambridge.org/us/dictionary/english/"+word
    response = requests.get(url,headers={ "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" })
    return BeautifulSoup(response.text, "html.parser")

def get_def(bs_obj):
    text = bs_obj.select_one("div .def.ddef_d.db")
    definition = []
    for t in text:
        if t.string.strip() != '':
            definition.append(t.string.strip())
    temp = " ".join(definition)
    if temp[-1:] == ':':
        temp = temp[:-1]
    return temp

def get_example(bs_obj):
    # text = bs_obj.select_one("div .examp.dexamp").select_one("span")
    # example = []
    # for t in text:
    #     if t.string.strip() != '':
    #         example.append(t.string.strip())
    # return " ".join(example)
    text = bs_obj.find('div', class_="examp dexamp").get_text()
    pos = text.find(r']')
    text = text[(pos+1):].strip()
    return text
  
def get_property(word):
    try:
        print("------------Get Property: ", word, "------------")
        word_property = {}
        try:
            word_property['pos'] =  tagdict[get_pos(word)][0] #get_pos(word)
        except:
            print("Error - pos")
            word_property['pos'] = ' '
        try:
            word_property['origin'] = get_origin(word)
        except:
            print("Error - origin")
            word_property['origin'] = ' '
        try:
            word_property['segment'] = get_verb_segment(word) if word_property['pos'].startswith('V') else get_segment(word)
        except:
            print("Error - segment")
            word_property['segment'] = ' '
        try:
            bs_obj = get_bs_object(word_property['origin'])
        except:
            print("Error - bs_obj")
        try:
            word_property['definition'] = get_def(bs_obj)
        except:
            print("Error - definition")
            word_property['definition'] = "The vocabulary you used is too trendy and has not yet been defined"
        try:                   
            word_property['example'] = get_example(bs_obj)
        except:
            print("Error - example")
            word_property['example'] = "Please use your imagination to think about your own example sentences"
        return word_property
    except:
        print("Error - property")
        return None


sentence = ""
def set_sentence(s):
    global sentence 
    sentence = s
    return
    
def get_sentence():
    return sentence


candicated_string = set([',', ':', '.', '"','@','#','$'])
stop_words = set(stopwords.words('english'))  

def response(sentence):
    tokens = "".join([_ for _ in sentence if _ not in candicated_string]).split(" ")
    global pos_dict
    pos_dict = dict(pos_tag(tokens))
    filtered_sentence = [w for w in tokens if not w.lower() in stop_words]
    r = dict()
    for _ in filtered_sentence:
        #print(np.array(word_p(_)))
        p = get_property(_)
        if p == None:
            continue 
        r[_] = p
        # print(_)
        # print(p)
        # print()
    return r 





