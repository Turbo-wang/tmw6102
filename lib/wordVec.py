# -*- coding=utf-8 -*-
import numpy as np
from scipy.spatial.distance import cosine

def load_wordVec_mem(vector_file):
    vector_dict = {}
    with open(vector_file) as vector:
        wordslist = vector.readlines()
        for word in wordslist:
            tmp = word.split()
            vector_dict[tmp[0]] = tmp[1:]
    return vector_dict

def distence_two_vect(word1, word2, method= 'Cosine'):
    # method = method
    vect1 = np.asarray(word1, dtype='float64')
    vect2 = np.asarray(word2, dtype='float64')
    distence = 0
    if method == 'Cosine':
        distence = cosine(vect1, vect2)
    elif method == 'Jaccard':
        pass
    elif method == 'Euclidean':
        pass
    elif method == 'CrossEntropy':
        pass
    else:
        raise NameError("no such method:"+method)
    return distence

