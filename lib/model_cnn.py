# from __future__ import print_function
import numpy as np
np.random.seed(1337)  # for reproducibility

from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Lambda
from keras.layers.embeddings import Embedding
from keras.layers.convolutional import Convolution1D
from keras.layers import Merge

from keras import backend as K
import sys
import os
import pickle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import wordVec
import utils.train_utils
import utils.process_sentence as process_sentence

max_features = 5000
word_len = 10000
# maxlen = 10000
batch_size = 32
embedding_dims = 200
nb_filter = 250
filter_length = 2
hidden_dims = 250
nb_epoch = 1

def prapare_train():
    en_vec_dict = wordVec.load_wordVec_mem('../data/envec.txt')
    fr_vec_dict = wordVec.load_wordVec_mem('../data/frvec.txt')
    dict_url_text, dict_url_en, dict_url_fr = utils.train_utils.extract_text()
    
    train_file = open('../data/train_matrix.out','w')
    test_file = open('../data/test_matrix.out','w')
    
    X_train = []
    Y_train = []
    X_test = []
    Y_test = []
    with open('../data/train_data.pairs') as train_lines:
        for line in train_lines:
            line.split()
            Y_train.append(line[0])
            
            text = dict_url_text.setdefault(line[1], None)
            if text is not None:
                #if isinstance(text, unicode):
                text = text.replace('\n','\t')
                text = process_sentence.tokenize(text)
            else:
                #print en_url
                text = []
            en_text_list = text
            x_ = []
            for word in en_text_list:
                x_.append(en_vec_dict.setdefault(word, [0]*200))
            if len(en_text_list) < 10000:
                for i in range(10000-len(en_text_list)):
                    x_.append([0]*200)
            text = dict_url_text.setdefault(line[2], None)
            if text is not None:
                #if isinstance(text, unicode):
                text = text.replace('\n','\t')
                text = process_sentence.tokenize(text)
            else:
                #print en_url
                text = []
            fr_text_list = text
            for word in fr_text_list:
                x_.append(fr_vec_dict.setdefault(word, [0]*200))
            if len(fr_text_list) < 10000:
                for i in range(10000-len(fr_text_list)):
                    x_.append([0]*200)
            X_train.append(x_)

    pickle.dump(X_train, train_file)
    print 'pickle train ok'
    # with open('../data/dev_data.pairs') as train_lines:
    #     for line in train_lines:
    #         line.split()
    #         Y_test.append(line[0])
    #         text = dict_url_text.setdefault(line[1], None)
    #         if text is not None:
    #             #if isinstance(text, unicode):
    #             text = text.replace('\n','\t')
    #             text = process_sentence.tokenize(text)
    #         else:
    #             #print en_url
    #             text = []
    #         en_text_list = text
    #         x_ = []
    #         for word in en_text_list:
    #             x_.append(en_vec_dict.setdefault(word, [0]*200))
    #         if len(en_text_list) < 10000:
    #             for i in range(10000-len(en_text_list)):
    #                 x_.append([0]*200)
    #         text = dict_url_text.setdefault(line[2], None)
    #         if text is not None:
    #             #if isinstance(text, unicode):
    #             text = text.replace('\n','\t')
    #             text = process_sentence.tokenize(text)
    #         else:
    #             #print en_url
    #             text = []
    #         fr_text_list = text
    #         for word in fr_text_list:
    #             x_.append(fr_vec_dict.setdefault(word, [0]*200))
    #         if len(fr_text_list) < 10000:
    #             for i in range(10000-len(fr_text_list)):
    #                 x_.append([0]*200)
    #         X_test.append(x_)

    # pickle.dump(X_test, test_file)
    # print 'pickle test ok'
    return (X_train, Y_train, X_test, Y_test)

def train_model():
    # (X_train, Y_train, X_test, Y_test) = prapare_train()
    X_train = pickle.load('../data/train_matrix.out')
    X_test = pickle.load('../data/train_matrix.out')
    Y_train = [1,0,0]*1300
    Y_test = [1,0,0]*324
    print len(X_train) - len(Y_train)
    print len(X_test) - len(Y_test)
    # model = Sequential()
    # model = get_nn_model()
    # model.compile(loss='binary_crossentropy',
    #             optimizer='adam',
    #             metrics=['accuracy'])
    # model.fit(X_train, Y_train,
    #       batch_size=batch_size,
    #       nb_epoch=nb_epoch,
    #       validation_data=(X_test, Y_test))
    # print 'ok'

def get_nn_model():
    # (X_train, Y_train, X_test, Y_test) = prapare_train()
    print('Build model...')
    model_en = Sequential()
    model_en.add(Embedding(max_features,
                    embedding_dims,
                    input_length=maxlen,
                    dropout=0.2))
    model_en.add(Convolution1D(nb_filter=nb_filter,
                            filter_length=filter_length,
                            border_mode='valid',
                            activation='relu',
                            subsample_length=1))
    def max_1d(X):
        return K.max(X, axis=1)

    model_en.add(Lambda(max_1d, output_shape=(nb_filter,)))

    # We add a vanilla hidden layer:
    model_en.add(Dense(hidden_dims))
    model_en.add(Dropout(0.2))
    model_en.add(Activation('relu'))

    model_fr = Sequential()
    model_fr.add(Embedding(max_features,
                    embedding_dims,
                    input_length=maxlen,
                    dropout=0.2))
    model_fr.add(Convolution1D(nb_filter=nb_filter,
                            filter_length=filter_length,
                            border_mode='valid',
                            activation='relu',
                            subsample_length=1))
    model_fr.add(Lambda(max_1d, output_shape=(nb_filter,)))
    model_fr.add(Dense(hidden_dims))
    model_fr.add(Dropout(0.2))
    model_fr.add(Activation('relu'))

    merged = Merge([model_en, model_fr], mode='concat')

    final_model = Sequential()
    final_model.add(merged)
    final_model.add(Dense(2, activation='softmax'))

    return final_model

if __name__ == '__main__':
    train_model()