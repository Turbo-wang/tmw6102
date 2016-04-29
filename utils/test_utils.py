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

def load_translation(file_name):
    url_dict = {}
    domain  = file_name[:-8]
    print domain
    with open('../data/en_train_trans.out') as en_train_trans:
        flag = False
        lines = en_train_trans.readlines()
        for url, text in zip(lines[::2],lines[1::2]):
            url = url.strip()
            text = text.strip()
            # line_url = en_train_trans.readline()
            # # print line_url
            # line_text = en_train_trans.readline()
            if re.search(domain, url) != None:
                url_dict[url] = process_sentence.tokenize_text(text)
            #     flag = True
            #     # print line_url, files_name
            # elif flag == True:
            #     break
    # print url_dict
    return url_dict

def bleu_test():
    files_list = [f for f in listdir(corpora_dir) if isfile(join(corpora_dir, f)) and (f.endswith('lett') or f.endswith('gz'))]
    match_url = []
    count = 0
    with open('../data/train.pairs') as pairs:
        for pair in pairs:
            match_url.append(pair)
    predict_file = open('../data/predict_unlimit.pairs','w')

    for file_name in files_list[:1]: 
        url_text_trans = load_translation(file_name)  
        print file_name,len(url_text_trans) 
        dict_url_text, dict_url_en, dict_url_fr = extract_domain(file_name)
        en_text_list = []
        print 'extract ok'
        reference_list = []
        time_start = time.time()
        for url in dict_url_fr:
            pos = -1
            score_list = []
            text = url_text_trans[url]
            for en_url in dict_url_en:
                en_text = process_sentence.tokenize_text(dict_url_text[en_url])
                # print en_text
                score_list.append(sentence_bleu(en_text, text))
            print max(score_list)
            pos = score_list.index(max(score_list))
            # if pos >= len(dict_url_en):
            #     print "pos error at", url,'\t',en_url
            #     continue
            # if pos < 0:
            #     print 'pos < 0 at', url,'\t',en_url
            en_url_pred = dict_url_en[pos]
            pre = str(en_url_pred) + '\t' + str(url)
            print pre
            predict_file.write(pre)
            predict_file.write('\n')
            if pre in match_url:
                count +=1
        time_end = time.time()
        print (time_end - time_start),'for',file_name,'\t',count
    predict_file.close()
    print count

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