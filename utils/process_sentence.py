import nltk.tokenize
import train_utils
import math
import matplotlib.pyplot as plt

def tokenize(text, length = 10000):
    _tokenizer = nltk.tokenize.RegexpTokenizer(pattern=r'[\w\$]+|[^\w\s]')
    tokens = _tokenizer.tokenize(text.lower())
    if len(tokens) > length:
        tokens = tokens[:10000]
    return tokens

def statistic_web():
    #dict_url = train_utils.extract_text()
    length_list = []
    thefile = open('../data/length_list.out','w')
    with open('../data/train.pairs') as train_file:
        # lines = train_file.readlines()
        for line in train_file:
            pairs = line.strip().split()
            print len(pairs)
            en_url = pairs[0]
            fr_url = pairs[1]
            en_text = train_utils.get_doc_by_url(en_url)
            fr_text = train_utils.get_doc_by_url(fr_url)
            length_list.append(len(en_text))
            thefile.write(len(en_text))
            thefile.write('\t')
            thefile.write(len(fr_text))
            thefile.write('\n')
            length_list.append(len(fr_text))
    return length_list

def analysis():
    length_en_list = []
    length_fr_list = []
    flag = False
    with open('../data/length_list.out') as length_list:
        for length in length_list:
           
            if flag == False:
                print math.log10(float(length))
                length_en_list.append(math.log10(float(length)))
                flag = True
            else:
                length_fr_list.append(math.log10(float(length)))
                flag = False
    x = [x for x in range(len(length_en_list))]
    dislist  = []
    for en,fr in zip(length_en_list, length_fr_list):
        dis = abs(int(en)-int(fr))
        dislist.append(dis)
    plt.plot(x,length_en_list,'b',x,length_fr_list,'g',x,dislist,'r')
    plt.show()




if __name__ == "__main__":
    analysis()