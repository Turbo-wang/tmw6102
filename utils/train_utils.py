from os import listdir
from os.path import isfile, join
import base64
import gzip
import sys
import numpy
import os
import random
import re
import time

# sys.path.append("../")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import configs.config
# import lib.model_cnn
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
                dict_url_text[line.url.encode('utf-8')] = line.text.encode('utf-8')
                dict_url_en.append(line.url.encode('utf-8'))
        elif line.lang == 'fr':
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

def bleu_test():
    files_list = [f for f in listdir(corpora_dir) if isfile(join(corpora_dir, f)) and (f.endswith('lett') or f.endswith('gz'))]
    match_url = []
    count = 0
    with open('../data/train.pairs') as pairs:
        for pair in pairs:
            match_url.append(pair)
    predict_file = open('../data/predict_unlimit.pairs','w')

    for file_name in files_list:    
        dict_url_text, dict_url_en, dict_url_fr = extract_domain(file_name)
        en_text_list = []
        print 'extract ok'
        reference_list = []
                # en_text_list.append(text)
        
        
        time_start = time.time()
        for url in dict_url_fr:
            pos = -1
            score_list = []
            text = process_sentence.tokenize_text(dict_url_text[url])
            for en_url in dict_url_en:
                en_text = process_sentence.tokenize_text(dict_url_text[en_url])
                score_list.append(sentence_bleu(en_text, text))
            pos = score_list.index(max(score_list))
            if pos >= len(dict_url_en):
                print "pos error at", url,'\t',en_url
                continue
            if pos < 0:
                print 'pos < 0 at', url,'\t',en_url
            en_url_pred = dict_url_en[pos]
            pre = str(en_url_pred) + '\t' + str(url)
            predict_file.write(pre)
            predict_file.write('\n')
            if pre in match_url:
                count +=1
        time_end = time.time()
        print (time_end - time_start),'for',file_name,'\t',count
    predict_file.close()
    print count


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
        print url

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
        # pairs = file.readlines()
        # for pair in pairs:
        #     print pair
        #     url_pair = pair.split()
        #     en_url = url_pair[0]
        #     fr_url = url_pair[1]
        #     en_text = get_doc_by_url(en_url)
        #     fr_text = get_doc_by_url(fr_url)
        #     par_en.write(en_url)
        #     par_en.write('\n')
        #     if en_text is not None:
        #         if isinstance(en_text, unicode):
        #             # text = en_text.replace('\n','\t')
        #         # par_en.write('1')
        #         # par_en.write('\t')
        #         # par_en.write(en_url)
        #         # par_en.write('\t')
        #             par_en.write(en_text)
        #         else:
        #             par_en.write(en_text.decode('utf-8'))
        #         par_en.write('\n')
        #     else:
        #         #print en_url
        #         par_en.write('\n')

        #     par_fr.write(fr_url)
        #     par_fr.write('\n')
        #     if fr_text is not None:
        #         if isinstance(fr_text, unicode):
        #             # text = text.replace('\n','\t')
        #         # par_fr.write('1')
        #         # par_fr.write('\t')
        #         # par_fr.write(fr_url)
        #         # par_fr.write('\t')

        #             par_fr.write(fr_text)
        #         else:
        #             par_fr.write(fr_text.decode('utf-8'))
        #         par_fr.write('\n')
        #     else:
        #         par_fr.write('\n')
    



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
# dict_url_text, dict_url_en, dict_url_fr = extract_text()
# 
if __name__ == '__main__':
    get_translation_for_url()
    # bleu_test()
    # text_url_dict = extract_text()
    
    # with open('../data/train.pairs') as file:
    #     pairs = file.readlines()
    #     for pair in pairs:
    #         eng_url , fr_url = pair.split('\t')
    #         eng_text = text_url_dict[eng_url]
    #         fr_text = text_url_dict[fr_url]
    #         