#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import gzip
import sys
from collections import namedtuple

Page = namedtuple("Page", "url, html, text, mime_type, encoding, lang")

def read_lett_iter(f, decode = True):
    pass

def decode_file(file):
    fh = file
    flag = False
    if file.endswith('gz'):
        print 'ok'
        flag = True
        #fh = gzip.GzipFile(fileobj = fh, mode = 'r')
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

if __name__ == "__main__":
    #write_file = "bugadacargnel.com.lett.decode"
    write_file = "schackportalen.nu.lett.decode"
    wf = open(write_file, 'w')
    count =1
    for i in decode_file("schackportalen.nu.lett.gz"):
        if i.lang == 'fr' or i.lang == 'en':
            count +=1
        wf.write(i.url.encode('utf-8'))
        wf.write("\t")
        wf.write(i.html.encode('utf-8'))
        wf.write("\t")
        wf.write("-----------text------------")
        wf.write(i.text.encode('utf-8'))
        wf.write("-----------text------------")
        wf.write("\t")
        wf.write(i.mime_type.encode('utf-8'))
        wf.write("\t")
        wf.write(i.encoding.encode('utf-8'))
        wf.write("\t")
        wf.write(i.lang.encode('utf-8'))
        wf.write("\n")
        wf.write("--------------devide---------------")
        wf.write("\n")
        #print i.url, i.html, i.text, i.mime_type, i.encoding, i.lang
    wf.close()
    print count
