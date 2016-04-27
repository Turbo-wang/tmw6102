from os import listdir
from os.path import isfile, join
import base64
import gzip
import sys
import numpy
import os
import random
import re

# sys.path.append("../")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import configs.config
# import lib.model_cnn

from collections import namedtuple

Page = namedtuple("Page", "url, html, text, mime_type, encoding, lang")

corpora_dir = configs.config.CORPORA_DIR
file_eng = configs.config.CORPUS_ENG
file_fr = configs.config.CORPUS_FR


def extract_domain(file):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    dict_url_text = {}
    dict_url_en = []
    dict_url_fr = []
    #outputfile = open('extract_text.out', 'w')
    # files_list = [f for f in listdir(corpora_dir) if isfile(join(corpora_dir, f)) and (f.endswith('lett') or f.endswith('gz'))]
    # if write_file == 1:
    #     wf_eng = open(join(corpora_dir,file_eng), 'w')
    #     wf_fr = open(join(corpora_dir,file_fr), 'w')    
    # for file in files_list:
    # print file
    for line in decode_file(join(corpora_dir, file)):
        if line.lang == 'fr':
            if isinstance(line.text, unicode):
                dict_url_text[line.url] = line.text
                dict_url_en.append(line.url)
            else:
                dict_url_text[line.url.encode('utf-8')] = line.text.encode('utf-8')
                dict_url_en.append(line.url.encode('utf-8'))
        elif line.lang == 'en':
            if isinstance(line.text, unicode):
                dict_url_text[line.url] = line.text
                dict_url_fr.append(line.url)
            else:
                dict_url_text[line.url.encode('utf-8')] = line.text.encode('utf-8')
                dict_url_fr.append(line.url.encode('utf-8'))
        else:
            continue
    # print 'ok'
    return dict_url_text, dict_url_en, dict_url_fr

def extract_text(write_file = 0):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    dict_url_text = {}
    dict_url_en = []
    dict_url_fr = []
    #outputfile = open('extract_text.out', 'w')
    files_list = [f for f in listdir(corpora_dir) if isfile(join(corpora_dir, f)) and (f.endswith('lett') or f.endswith('gz'))]
    if write_file == 1:
        wf_eng = open(join(corpora_dir,file_eng), 'w')
        wf_fr = open(join(corpora_dir,file_fr), 'w')    
    for file in files_list:
        # print file
        for line in decode_file(join(corpora_dir, file)):
            if line.lang == 'fr':
                if isinstance(line.text, unicode):
                    dict_url_text[line.url] = line.text
                    dict_url_en.append(line.url)
                else:
                    dict_url_text[line.url.encode('utf-8')] = line.text.encode('utf-8')
                    dict_url_en.append(line.url.encode('utf-8'))
                if write_file == 1:
                    wf_fr.write(line.text.encode('utf-8'))
                    wf_fr.write('\n')
            elif line.lang == 'en':
                if isinstance(line.text, unicode):
                    dict_url_text[line.url] = line.text
                    dict_url_en.append(line.url)
                else:
                    dict_url_text[line.url.encode('utf-8')] = line.text.encode('utf-8')
                    dict_url_fr.append(line.url.encode('utf-8'))
                if write_file == 1:
                    wf_eng.write(line.text.encode('utf-8'))
                    wf_eng.write('\n')
            else:
                continue
    if write_file == 1:
        wf_eng.close()
        wf_fr.close()
    print 'extract all file ok'
    return dict_url_text, dict_url_en, dict_url_fr



def get_doc_by_url(url):
    

    #url_pair = pair.split()
    #en_url = url_pair[0]
    #fr_url = url_pair[1]
    text = dict_url_text.setdefault(url, None)
    if text is not None:
        #if isinstance(text, unicode):
        text = text.replace('\n','\t')
    else:
        print url

    return text

def get_para_text():
    par_en = open('../data/para.en','w')
    par_fr = open('../data/para.fr','w')
    
    with open('../data/train.pairs') as file:
        pairs = file.readlines()
        for pair in pairs:
            print pair
            url_pair = pair.split()
            en_url = url_pair[0]
            fr_url = url_pair[1]
            en_text = get_doc_by_url(en_url)
            fr_text = get_doc_by_url(fr_url)
            par_en.write(en_url)
            par_en.write('\n')
            if en_text is not None:
                if isinstance(en_text, unicode):
                    # text = en_text.replace('\n','\t')
                # par_en.write('1')
                # par_en.write('\t')
                # par_en.write(en_url)
                # par_en.write('\t')
                    par_en.write(en_text)
                else:
                    par_en.write(en_text.decode('utf-8'))
                par_en.write('\n')
            else:
                #print en_url
                par_en.write('\n')

            par_fr.write(fr_url)
            par_fr.write('\n')
            if fr_text is not None:
                if isinstance(fr_text, unicode):
                    # text = text.replace('\n','\t')
                # par_fr.write('1')
                # par_fr.write('\t')
                # par_fr.write(fr_url)
                # par_fr.write('\t')

                    par_fr.write(fr_text)
                else:
                    par_fr.write(fr_text.decode('utf-8'))
                par_fr.write('\n')
            else:
                par_fr.write('\n')
    
    par_en.close()
    par_fr.close()


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


def compose_train_data():
    train_data = open('../data/train_data.pairs','w')
    # dev_data = open('../data/dev_data.pairs','w')

    #re_obj = re.compile('((http|https)://(\w+\\.?)+?/)')
    re_obj = re.compile('((?<=http://)(\w+-?\w\\.?)+?(?=/))')



    with open('../data/train.pairs') as train_file:
        lines = train_file.readlines()

        for line in lines[:1300]:
            line = line.strip().split()
            print line
            domain = re_obj.findall(line[0])

            print domain[0][0]
            domainfile = str(domain[0][0]) + '.lett.gz'
            dict_domain, dict_url_domain_en, dict_url_domain_fr = extract_domain(domainfile)
            train_data.write('1')
            train_data.write('\t')
            train_data.write(line[0])
            train_data.write('\t')
            train_data.write(line[1])
            train_data.write('\n')

            train_data.write('0')
            train_data.write('\t')
            train_data.write(line[0])
            train_data.write('\t')
            error_url = line[0]
            url_num = len(dict_url_domain_en)
            while True:
                index = random.randint(0,url_num-1)
                error_url = dict_url_domain_en[index]
                if error_url != line[0]:
                    break
            train_data.write(error_url)
            train_data.write('\n')

            train_data.write('0')
            train_data.write('\t')
            error_url = line[1]
            url_num = len(dict_url_domain_fr)
            while True:
                index = random.randint(0,url_num-1)
                error_url = dict_url_domain_fr[index]
                if error_url != line[1]:
                    break
            train_data.write(error_url)
            train_data.write('\t')
            train_data.write(line[1])
            train_data.write('\n')

        # for line in lines[1300:]:
        #     line = line.strip().split()
        #     print line
        #     domain = re_obj.findall(line[0])

        #     print domain[0][0]
        #     domainfile = str(domain[0][0]) + '.lett.gz'
        #     dict_domain, dict_url_domain_en, dict_url_domain_fr = extract_domain(domainfile)
        #     dev_data.write('1')
        #     dev_data.write('\t')
        #     dev_data.write(line[0])
        #     dev_data.write('\t')
        #     dev_data.write(line[1])
        #     dev_data.write('\n')

        #     dev_data.write('0')
        #     dev_data.write('\t')
        #     dev_data.write(line[0])
        #     dev_data.write('\t')
        #     error_url = line[0]
        #     url_num = len(dict_url_domain_en)
        #     while True:
        #         index = random.randint(0,url_num-1)
        #         error_url = dict_url_domain_en[index]
        #         if error_url != line[0]:
        #             break
        #     dev_data.write(error_url)
        #     dev_data.write('\n')

        #     dev_data.write('0')
        #     dev_data.write('\t')
        #     error_url = line[1]
        #     url_num = len(dict_url_domain_fr)
        #     while True:
        #         index = random.randint(0,url_num-1)
        #         error_url = dict_url_domain_fr[index]
        #         if error_url != line[1]:
        #             break
        #     dev_data.write(error_url)
        #     dev_data.write('\t')
        #     dev_data.write(line[1])
        #     dev_data.write('\n')


def calculate_vector_text(text):
    eng_vector_dict = lib.load_wordVec_mem('../data/envec.txt')
    fr_vector_dict = lib.load_wordVec_mem('../data/frvec.txt')
    vector = np.zeros()
    # for word in text:
dict_url_text, dict_url_en, dict_url_fr = extract_text()
# dict_url_text, dict_url_en, dict_url_fr = extract_text()
if __name__ == '__main__':
    #get_para_text()
    get_para_text()
    # text_url_dict = extract_text()
    
    # with open('../data/train.pairs') as file:
    #     pairs = file.readlines()
    #     for pair in pairs:
    #         eng_url , fr_url = pair.split('\t')
    #         eng_text = text_url_dict[eng_url]
    #         fr_text = text_url_dict[fr_url]
    #         