from os import listdir
from os.path import isfile, join
import base64
import gzip
import sys
import numpy
import os
import random
import re
import pickle
# sys.path.append("../")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import configs.config
# import lib.model_cnn

from collections import namedtuple

corpora_dir = configs.config.TEST_DIR
unzip_files_dir = configs.config.TEST_DIR_UNZIP

Page = namedtuple("Page", "url, html, text, mime_type, encoding, lang")

def extract_domain(file):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    dict_url_text_en = {}
    dict_url_text_fr = {}
    for line in decode_file(join(corpora_dir, file)):
        if line.lang == 'fr':
            if isinstance(line.text, unicode):
                dict_url_text_fr[line.url] = line.text
                # dict_url_en.append(line.url)
            else:
                dict_url_text_fr[line.url.encode('utf-8')] = line.text.encode('utf-8')
                # dict_url_en.append(line.url.encode('utf-8'))
        elif line.lang == 'en':
            if isinstance(line.text, unicode):
                dict_url_text_en[line.url] = line.text
                # dict_url_fr.append(line.url)
            else:
                dict_url_text_en[line.url.encode('utf-8')] = line.text.encode('utf-8')
                # dict_url_fr.append(line.url.encode('utf-8'))
        else:
            continue
    # print 'ok'
    return dict_url_text_fr, dict_url_text_en

def extract_all():
    # files_list = [f for f in listdir(corpora_dir) if isfile(join(corpora_dir, f)) and f.endswith('gz')]
    files_list = ["www.conidia.fr.lett.gz"]
    for file in files_list:
        extract_dict_fr, extract_dict_en = extract_domain(file)
        file_name = "".join(list(file)[:-3])
        file_name_en = file_name+'.en'
        file_name_fr = file_name+'.fr'
        with open(join(unzip_files_dir,file_name_en), 'w') as file_p:
            pickle.dump(extract_dict_en, file_p, pickle.HIGHEST_PROTOCOL)
        with open(join(unzip_files_dir,file_name_fr), 'w') as file_p:
            pickle.dump(extract_dict_fr, file_p, pickle.HIGHEST_PROTOCOL)
    print 'ok'

def generate_pairs(file_name):
    abs_distance = 10
    file_name_en = file_name+'.en'
    file_name_fr = file_name+'.fr'
    with open(join(unzip_files_dir,file_name_en),'r') as file_p:
        extract_dict_en = pickle.load(file_p)
    with open(join(unzip_files_dir,file_name_fr), 'r') as file_p:
        extract_dict_fr = pickle.load(file_p)
    en_list = extract_dict_en.keys()
    fr_list = extract_dict_fr.keys()
    print len(extract_dict_en)
    print len(extract_dict_fr)
    count = 0
    with open(join(unzip_files_dir, file_name+".pairs"), 'w') as f:
        for en_web in en_list:
            length_en = len(en_web)
            abs_distance = length_en / 5
            for fr_web in fr_list:
                
                
                if abs(len(extract_dict_en[en_web]) - len(extract_dict_fr[fr_web])) < abs_distance:
                    count +=1
                    print count
                    print en_web,'\t',fr_web
                    f.write(en_web)
                    f.write('\t')
                    f.write(fr_web)
                    f.write('\n')

def decode_file(file):
    fh = file
    flag = False
    if file.endswith('gz'):
        flag = True
    if flag:
        f = gzip.open(fh)
    else:
        f = open(fh)
    for line in f:
        lang, mime, enc, url, html, text = line.split("\t")

        html = base64.b64decode(html)
        text = base64.b64decode(text)
        html = html.decode("utf-8")
        text = text.decode("utf-8")

        p = Page(url, html, text, mime, enc, lang)
        yield p
    f.close()

def get_translation_for_url():
    text_list = []
    url = " "
    url_last = "http://1d-aquitaine.com/"
    en_text_trans = open('../data/test/en_text_trans.out','w')
    with open('../data/test/translations.test/url2text.en') as en_lines:
        for line in en_lines:
            content = line.split()
            url_new = content[0]
            text = '\t'.join(content[1:])
            if url_last == url_new:
                text_list.append(text)
            else:
                # print url_last
                en_text_trans.write(url_last)
                en_text_trans.write('\n')
                en_text_trans.write('\t'.join(text_list))
                en_text_trans.write('\n')
                url_last = url_new
                text_list = []
    en_text_trans.close()

if __name__ == '__main__':
    # extract_all()
    # print 'extract_all'
    # generate_pairs('www.conidia.fr.lett')
    get_translation_for_url()