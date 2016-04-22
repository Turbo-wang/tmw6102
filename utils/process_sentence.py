import nltk.tokenize
import train_utils
# import matplotlib.

def tokenize(text):
    _tokenizer = nltk.tokenize.RegexpTokenizer(pattern=r'[\w\$]+|[^\w\s]')
    tokens = _tokenizer.tokenize(text.lower())
    return tokens

def statistic_web():
    #dict_url = train_utils.extract_text()
    length_list = []
    thefile = open('../data/length_list.out','w')
    with open('../data/train.pairs') as train_file:
        lines = train_file.readlines()
        for line in lines:
            pairs = line.strip().split()
            print len(pairs)
            en_url = pairs[0]
            fr_url = pairs[1]
            en_text = train_utils.get_doc_by_url(en_url)
            fr_text = train_utils.get_doc_by_url(fr_url)
            length_list.append(len(en_text))
            length_list.append(len(fr_text))
    for item in length_list:
        thefile.write("%s\n" % item)

if __name__ == "__main__":
    statistic_web()