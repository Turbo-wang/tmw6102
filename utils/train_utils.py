from os import listdir
from os.path import isfile, join
import base64
import gzip
import sys
reload(sys)
sys.path.append("../")
sys.setdefaultencoding('utf-8')
import configs.config
from collections import namedtuple

Page = namedtuple("Page", "url, html, text, mime_type, encoding, lang")

corpora_dir = configs.config.CORPORA_DIR
file_eng = configs.config.CORPUS_ENG
file_fr = configs.config.CORPUS_FR

def extract_text():
    dict_url_text = {}
    #outputfile = open('extract_text.out', 'w')
    files_list = [f for f in listdir(corpora_dir) if isfile(join(corpora_dir, f)) and (f.endswith('lett') or f.endswith('gz'))]
    
    wf_eng = open(join(corpora_dir,file_eng), 'w')
    wf_fr = open(join(corpora_dir,file_fr), 'w')    
    for file in files_list:
        print file
        for line in decode_file(join(corpora_dir, file)):
            if line.lang == 'fr':
                if isinstance(line.text, unicode):
                    dict_url_text[line.url] = line.text
                else:
                    dict_url_text[line.url.encode('utf-8')] = line.text.encode('utf-8')
                # wf_fr.write(line.text.encode('utf-8'))
                # wf_fr.write('\n')
            elif line.lang == 'en':
                if isinstance(line.text, unicode):
                    dict_url_text[line.url] = line.text
                else:
                    dict_url_text[line.url.encode('utf-8')] = line.text.encode('utf-8')
                # wf_eng.write(line.text.encode('utf-8'))
                # wf_eng.write('\n')
            else:
                continue

    wf_eng.close()
    wf_fr.close()
    print 'ok'
    return dict_url_text

def get_para_text():
    par_en = open('para.en','w')
    par_fr = open('para.fr','w')
    dict_url_text = extract_text()
    with open('../data/train.pairs') as file:
        pairs = file.readlines()
        for pair in pairs:
            print pair
            url_pair = pair.split()
            en_url = url_pair[0]
            fr_url = url_pair[1]
            text = dict_url_text.setdefault(en_url, None)
            if text is not None:
                #if isinstance(text, unicode):
                par_en.write(text)
                #else:
                #    par_en.write(text.decode('utf-8'))
                par_en.write('\n')
            else:
                print en_url
            text = dict_url_text.setdefault(fr_url, None)
            if text is not None:
                #if isinstance(text, unicode):
                par_fr.write(text)
                #else:
                #    par_en.write(text.decode('utf-8'))
                par_fr.write('\n')
            else:
                print fr_url
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

if __name__ == '__main__':
    get_para_text()