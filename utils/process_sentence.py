from __future__ import print_function
from nltk.tokenize import word_tokenize
import train_utils
import math
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from nltk.tokenize import word_tokenize
# import matplotlib.pyplot as plt

def tokenize_text(text, length = 1000):
    # _tokenizer = nltk.tokenize.RegexpTokenizer('\w')
    tokens = word_tokenize(text.lower())
    if len(tokens) > length:
        tokens = tokens[:length]
    tokens_ = []
    for word in tokens:
        if re_obj.search(word):
            tokens_.append(word)
    return tokens_

def statistic_web():
    #dict_url = train_utils.extract_text()
    length_list = []
    thefile = open('../data/length_list.out','w')
    with open('../data/train.pairs') as train_file:
        # lines = train_file.readlines()
        for line in train_file:
            print(line)
            pairs = line.strip().split()
            en_url = pairs[0]
            fr_url = pairs[1]
            en_text = train_utils.get_doc_by_url(en_url)
            fr_text = train_utils.get_doc_by_url(fr_url)
            # length_list.append(len(en_text))
            thefile.write(str(len(en_text.split())))
            thefile.write('\t')
            thefile.write(str(len(fr_text.split())))
            thefile.write('\n')
    thefile.close()
            # length_list.append(len(fr_text))
    # return length_list

def analysis():
    length_en_list = []
    length_fr_list = []
    flag = False
    with open('../data/length_list.out') as length_list:
        for length in length_list:
            length = length.split()
            # if flag == False:
                # print math.log10(float(length))
            length_en_list.append(length[0])
                # length_en_list.append(math.log10(float(length)))
                # flag = True
            # else:
            length_fr_list.append(length[1])
                # length_fr_list.append(math.log10(float(length)))
                # flag = False
    x = [x for x in range(len(length_en_list))]
    dislist  = []
    count = 0
    alpha = 0.4
    for en,fr in zip(length_en_list, length_fr_list):
        en = en.strip()
        fr = fr.strip()
        dis = abs(int(en) - int(fr))
        dis_for = (int(en) * alpha + int(fr) * alpha) /2
        if (dis > dis_for):
            print(int(en),int(fr))
            count += 1
        dislist.append(dis)
    print(count)
    # plt.plot(x,dislist,'r')
    # plt.show()





if __name__ == "__main__":
    analysis()
