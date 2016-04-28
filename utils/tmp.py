import re

re_obj = re.compile('((?<=http://)(\w+-?\w\\.?)+?(?=/))')
para_en_for_train = open('../data/para_for_train.en','w')
para_fr_for_train = open('../data/para_for_train.fr','w')
with open('../data/para.en') as para_en:
    for line in para_en:
        if re.search('http://', line):
            continue
        else:
            para_en_for_train.write(line)

with open('../data/para.fr') as para_fr:
    for line in para_fr:
        if re.search('http://', line):
            continue
        else:
            para_fr_for_train.write(line)
para_en_for_train.close()
para_fr_for_train.close()