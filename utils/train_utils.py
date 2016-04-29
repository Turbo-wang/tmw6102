from __future__ import print_function
from os import listdir
from os.path import isfile, join
import base64
import gzip
import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
import numpy
import os
import random
import re
import time
import numpy as np
from scipy.spatial.distance import cosine
re_obj = re.compile('[a-zA-Z]')
# sys.path.append("../")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import configs.config
# import lib.model_cnn
from lib import wordVec
import process_sentence

from nltk.translate.bleu_score import corpus_bleu, sentence_bleu

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
        if line.lang == 'en':
            if isinstance(line.text, unicode):
                dict_url_text[line.url] = line.text
                dict_url_en.append(line.url)
            else:
                print(line.text)
                dict_url_text[line.url.encode('utf-8')] = line.text.encode('utf-8')
                dict_url_en.append(line.url.encode('utf-8'))
        elif line.lang == 'fr':
            if isinstance(line.text, unicode):
                dict_url_text[line.url] = line.text
                dict_url_fr.append(line.url)
            else:
                print(line.text)
                dict_url_text[line.url.encode('utf-8')] = line.text.encode('utf-8')
                dict_url_fr.append(line.url.encode('utf-8'))
        else:
            continue
    # print 'ok'
    return dict_url_text, dict_url_en, dict_url_fr

def text_from_translate(domain):
    pass

def get_translation_for_url():
    text_list = []
    url = " "
    url_last = 'http://bugadacargnel.com/fr/pages/presse.php?presse=19'
    en_text_trans = open('../data/en_train_trans.out','w')
    with open('../data/translations.train/url2text.en') as en_lines:
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

def load_translation(file_name):
    url_dict = {}
    domain  = file_name[:-8]
    print(domain)
    with open('../data/en_train_trans.out','r') as en_train_trans:
        flag = False
        lines = en_train_trans.readlines()
        for url, text in zip(lines[::2],lines[1::2]):
            url = url.strip()
            text = text.strip()
            # text = text.replace('\t',' ')
            # line_url = en_train_trans.readline()
            # # print line_url
            # line_text = en_train_trans.readline()
            if re.search(domain, url) != None:
                url_dict[url] = text
            #     flag = True
            #     # print line_url, files_name
            # elif flag == True:
            #     break
    # print url_dict
    return url_dict

def test():
    
    en_url = []
    en_url.append(enurl1)
    en_url.append(enurl2)
    en_url.append(enurl3)
    frurl = 'http://www.krn.org/fr/106.aspx'
    file_name = 'www.krn.org.lett.gz'
    url_text_trans = load_translation(file_name)  
    dict_url_text, dict_url_en, dict_url_fr = extract_domain(file_name)
    fr_text = url_text_trans[frurl]
    # fr_text = process_sentence.tokenize_text(fr_text)
    for enurl in en_url:
        en_text = dict_url_text[enurl]
        en_text = process_sentence.tokenize_text(en_text)
        print(sentence_bleu(en_text,fr_text))

def vector_test():
    en_vector_dict = wordVec.load_wordVec_mem('../data/envec2.txt')
    fr_vector_dict = wordVec.load_wordVec_mem('../data/frvec2.txt')
    files_list = [f for f in listdir(corpora_dir) if isfile(join(corpora_dir, f)) and (f.endswith('lett') or f.endswith('gz'))]
    match_url = []
    train_pair = []
    count = 0
    with open('../data/train.pairs','r') as pairs:
        for pair in pairs:
            train_pair.append(pair.strip())
            match_url += pair.strip().split()
    predict_file = open('../data/predict_unlimit.pairs','w')
    url_set = set(match_url)
    
    alpha = 0.35
    unk_vec_en = en_vector_dict['unknown']
    unk_vec_fr = fr_vector_dict['(unk)']
    count = 0
    for file_name in files_list[:1]: 
        file_name = 'www.krn.org.lett.gz'
        dict_url_text, dict_url_en, dict_url_fr = extract_domain(file_name)
        
        for fr_url in dict_url_fr:
            distance_list = []
            for en_url in dict_url_en:
                en_text = dict_url_text[en_url]
                en_length = len(en_text.strip().split())
                fr_text = dict_url_text[fr_url]
                fr_length = len(fr_text.strip().split())

                dis = abs(en_length - fr_length)
                dis_for = fr_length * alpha
                if (dis_for < dis):
                    continue

                en_text = process_sentence.tokenize_text(en_text)
                fr_text = process_sentence.tokenize_text(fr_text)

                en_web_vec = np.zeros(200)
                en_web_vec_length = len(en_text)
                for text in en_text:
                    vec = en_vector_dict.setdefault(text,unk_vec_en)
                    vec = np.asarray(vec, dtype='float32')
                    en_web_vec += vec
                    en_web_vec = np.divide(en_web_vec, float(en_web_vec_length))
                # print(en_web_vec)
                fr_web_vec = np.zeros(200)
                fr_web_vec_length = len(fr_text)
                for text in fr_text:
                    vec = fr_vector_dict.setdefault(text,unk_vec_fr)
                    vec = np.asarray(vec, dtype='float32')
                    fr_web_vec += vec
                    fr_web_vec = np.divide(fr_web_vec, float(fr_web_vec_length))
                # print(fr_web_vec)
                
                distance = cosine(en_web_vec,fr_web_vec)
                print(distance)
                tmp = []
                url_pair = en_url + '    ' + fr_url
                tmp.append(url_pair)
                tmp.append(distance)
                distance_list.append(tmp)
                predict_file.write(url_pair)
                predict_file.write('\t')
                predict_file.write(str(distance))
                predict_file.write('\n')
            distance_list = sorted(distance_list, key=lambda d:d[1])
            pre = distance_list[0][0]
            if pre in match_url:
                count +=1
                
            print(distance_list)


def get_sentence_vec(text):
    pass

def bleu_test():
    files_list = [f for f in listdir(corpora_dir) if isfile(join(corpora_dir, f)) and (f.endswith('lett') or f.endswith('gz'))]
    match_url = []
    train_pair = []
    count = 0
    with open('../data/train.pairs','r') as pairs:
        for pair in pairs:
            train_pair.append(pair.strip())
            match_url += pair.strip().split()
    predict_file = open('../data/predict_unlimit.pairs','w')
    url_set = set(match_url)
    
    alpha = 0.35
    for file_name in files_list[:1]: 
        file_name = 'www.krn.org.lett.gz'
        url_text_trans = load_translation(file_name)  
        
        dict_url_text, dict_url_en, dict_url_fr = extract_domain(file_name)
        en_text_list = []
        print('extract ok')
        reference_list = []
        

        for url in dict_url_fr:
            time_start = time.time()
            # if url in url_set:
            #     continue
            pos = -1
            score_list = []
            text = url_text_trans.setdefault(url, None)
            fr_length = len(text.strip().split())
            text = process_sentence.tokenize_text(text)
            for en_url in dict_url_en:
                # if en_url in url_set:
                #     continue
                en_text = dict_url_text[en_url]

                en_length = len(en_text.strip().split())

                dis = abs(en_length - fr_length)
                dis_for = fr_length * alpha
                if (dis_for < dis) or text == None:
                    continue
                en_text = process_sentence.tokenize_text(en_text)
                # print "en_text", text
                if len(en_text) != 0 and len(text) != 0:
                    url_pair = en_url+'    '+url
                    print('computing')

                    score = sentence_bleu(text,en_text)
                    tmp = []
                    tmp.append(url_pair)
                    tmp.append(score)
                    score_list.append(tmp)
            if len(score_list) != 0:
                score_list = sorted(score_list, key=lambda d:d[1],reverse = True)
                print(score_list)
                # pre = []
                for score in score_list[:5]:
                    pre = score[0]
                    score = score[1]
                    print(pre,'\tbleu', score)
                    predict_file.write(pre)
                    predict_file.write('\n')
                    # if pre in match_url:
                        # count +=1
            time_end = time.time()
            print((time_end - time_start),'for',url,'\t',count)
    predict_file.close()
    print(count)

def cal():
    count = 0
    with open('../data/predict_unlimit.pairs') as pre:
        with open('../data/train.pairs') as ans:
            for urls in pre:
                urls = urls.split()
                en_url = urls[0]
                fr_url = urls[1]
                for ans_urls in ans:
                    ans_urls = ans_urls.split()
                    en_ans = ans_urls[0]
                    fr_ans = ans_urls[1]
                    if en_url == en_ans and fr_url == fr_ans:
                        count += 1
    print(count)

def extract_text(write_file = 0):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    dict_url_text = {}
    dict_url_en = []
    dict_url_fr = []
    #outputfile = open('extract_text.out', 'w')
    files_list = [f for f in listdir(corpora_dir) if isfile(join(corpora_dir, f)) and (f.endswith('.lett') or f.endswith('.gz'))]
    if write_file == 1:
        wf_eng = open(join(corpora_dir,file_eng), 'w')
        wf_fr = open(join(corpora_dir,file_fr), 'w')    
    for file in files_list:
        print(file)
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
    print('extract all file ok')
    return dict_url_text, dict_url_en, dict_url_fr



def get_doc_by_url(url, dict_url_text):
    
    #url_pair = pair.split()
    #en_url = url_pair[0]
    #fr_url = url_pair[1]
    text = dict_url_text.setdefault(url, None)
    if text is not None:
        #if isinstance(text, unicode):
        # text = text.replace('\n','\t')
        pass
    else:
        print(url)

    return text

def get_para_text():
    par_en = open('../data/para_for_train.en','w')
    par_fr = open('../data/para_for_train.fr','w')
    with open('../data/test/translations.test/url2text.en') as en_file:
        with open('../data/test/translations.test/url2text.fr') as fr_file:
            for en_line, fr_line in zip(en_file,fr_file):
                en = en_line.split()
                en_url = en[0]
                en_text = '\t'.join(en[1:])
                fr = fr_line.split()
                fr_url = fr[0]
                fr_text = '\t'.join(fr[1:])
                par_en.write(en_text)
                par_en.write('\n')
                par_fr.write(fr_text)
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
        # print(line.split())
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
            print(line)
            domain = re_obj.findall(line[0])

            print(domain[0][0])
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
# dict_url_text, dict_url_en, dict_url_fr = extract_text()
# 
if __name__ == '__main__':
    vector_test()
    cal()
    # bleu_test()
    # text_url_dict = extract_text()
    
    # with open('../data/train.pairs') as file:
    #     pairs = file.readlines()
    #     for pair in pairs:
    #         eng_url , fr_url = pair.split('\t')
    #         eng_text = text_url_dict[eng_url]
    #         fr_text = text_url_dict[fr_url]
    #         