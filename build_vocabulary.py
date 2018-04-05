# -*- coding: utf-8 -*-

import sys
import os

import re
import io

# lang detection
from langdetect import detect

# split into sentences
import nltk 

from multiprocessing.pool import ThreadPool
from tqdm import tqdm # progressbar

reload(sys)
sys.setdefaultencoding("utf-8")


curr_dir_path = os.path.dirname(os.path.realpath(__file__))
TEXTS_DIR_PATH = os.path.join(curr_dir_path, "data/")
NUM_THREADS = 1

def is_bad_text(text):
    bad = False

    if text.strip() == "":
        bad = True

    if len(re.findall(r'[0-9]+', text)) > 0:
        bad = True
    if len(re.findall(r'[A-Za-z]+', text)) > 0:
        bad = True

    return bad


def build_vocabulary(output_path='vocabulary.txt'):

    # init lang detetor
    detect('test')

    sent_detector = nltk.data.load('nltk_data/russian.pickle') 

    def process_txt_file(b):
        sentences = []

        item_path = os.path.join(TEXTS_DIR_PATH, b)


        if item_path.split(".")[-1] != "txt":
            return []

        #print text

        # text_language = 'unknown'
        # try:
        #     text_language = detect(text[0:1500])
        # except:
        #     pass
            
        # if text_language != "ru":
        #     print 'skip not russian text (%s)' % text_language
        #     return []

        print "Loading file %s" % item_path
        f = open(item_path)
        text = f.read()
        f.close()
        print "Loaded file %s" % item_path

        print "Decoding text...."
        text = unicode(text, errors='ignore')
        print "Done decoding text"


        print 'Tokenizing text...'
        tokens = sent_detector.tokenize(text)        
        print "Done tokenizing: %i tokens found" % len(tokens)


        print "Filtering and processing tokens..."

        pbar = tqdm(total=len(tokens))

        for sent in tokens:
            pbar.update(1)

            if is_bad_text(sent):
                continue

            # convert linebreaks to spaces                    
            sent = sent.replace("\n", " ")
            # convert dashes to spaces
            sent = sent.replace("-", " ")
            # strip double spaces
            sent = re.sub(' +', ' ', sent)
            # to lowercase
            sent = sent.lower()
            # remove everything but russian letters and spaces
            sent = re.sub(u'[^а-яё ]', '', sent)
            # remove spaces on sides
            sent = sent.strip()
            #print sent
            sentences.append(sent)

            

        print "Successfully finished processing %s" % item_path
        
        return sentences

    
    pool = ThreadPool(NUM_THREADS)
    texts = pool.map(process_txt_file, os.listdir(TEXTS_DIR_PATH))

    sentences = []

    for text in texts:
        for sentence in text:
            sentences.append(sentence)

    
    print 'Writing sentences to %s' % output_path

    f = open(output_path, 'w+')
    f.write('\n'.join(sentences))    
    f.close()

    print 'Wrote %i sentences to %s' % (len(sentences), output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        build_vocabulary()
    else:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            print('USAGE: python build_vocabulary.py <vocabulary_output_file>')
        else:
            build_vocabulary(sys.argv[1])
        

