# -*- coding: utf-8 -*-
"""NLP_TR_LDA_MULTICORE(2).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hGWQ6rTW1AEms_-4g9XJ7hhrHLD5rha2
"""

import pandas as pd
import numpy as np
import nltk
import re
import warnings
from sklearn.datasets import fetch_20newsgroups
import nltk
!pip install progressbar2
from progressbar import ProgressBar
bar = ProgressBar()
nltk.download('stopwords')
WPT = nltk.WordPunctTokenizer()
stop_word_list = nltk.corpus.stopwords.words('english')

#Import Data
dataset =pd.read_csv("/content/drive/MyDrive/clean_data.csv")
data = dataset['0']
print(data[0])

!pip install gensim
import gensim
from gensim.utils import simple_preprocess
from nltk.stem import WordNetLemmatizer, SnowballStemmer

import nltk
nltk.download('wordnet')
import pandas as pd
from nltk.stem.snowball import SnowballStemmer
stemmer=SnowballStemmer('english')

def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(text):
    result=[]
    for token in gensim.utils.simple_preprocess(text) :
        if token not in stop_word_list and len(token) > 3:
            result.append(lemmatize_stemming(token))
     
    return result

def clean_data(data):
  data = data.replace('\n',' ')
  data = data.replace('\t',' ')
  data = data.map(lambda x: re.sub('[,\.\'!?();:$%&#"]', '', x))
  data = data.replace('\n','', regex=True)
  data = data.replace('\'','', regex=True)
  data = data.replace('-','', regex=True)
  data = data.replace('’','', regex=True)
  
  return data

import string
converted_list = []
data.astype(str)
data = data.astype(str) 
data=clean_data(data)

for element in data:
    element = element.translate(str.maketrans('','',string.punctuation))
    converted_list.append(element.strip())

processed_docs = []

for doc in bar(converted_list):
    processed_docs.append(preprocess(doc))

bigram = gensim.models.Phrases(processed_docs, min_count=5, threshold=100)
trigram = gensim.models.Phrases(bigram[processed_docs], threshold=100)  

bigram_mod = gensim.models.phrases.Phraser(bigram)
trigram_mod = gensim.models.phrases.Phraser(trigram)

print(trigram_mod[bigram_mod[processed_docs[0]]])

def make_bigrams(texts):
    return [bigram_mod[doc] for doc in texts]

def make_trigrams(texts):
    return [trigram_mod[bigram_mod[doc]] for doc in texts]

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    texts_out = []
    for sent in bar(texts):
        doc = nlp(" ".join(sent)) 
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out

import spacy
!pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.0/en_core_web_sm-2.2.0.tar.gz

data_words_trigrams = make_trigrams(processed_docs)

nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

data_lemmatized = lemmatization(data_words_trigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

dictionary = gensim.corpora.Dictionary(data_lemmatized)

count = 0                         #Testing if it is created
for k, v in dictionary.iteritems():
    print(k, v)
    count += 1
    if count > 10:
        break

'''
Remove very rare and very common words: (Probably not working for Turkish but I tried)
'''
dictionary.filter_extremes(no_below=15, no_above=0.1, keep_n= 100000)

'''
Create the Bag-of-words model for each document i.e for each document we create a dictionary reporting how many
words and how many times those words appear. Save this to 'bow_corpus'
'''
bow_corpus = [dictionary.doc2bow(doc) for doc in data_lemmatized]

'''
Preview BOW for our sample preprocessed document
'''
document_num = 20
bow_doc_x = bow_corpus[document_num]

for i in range(len(bow_doc_x)):
    print("Word {} (\"{}\") appears {} time.".format(bow_doc_x[i][0], 
                                                     dictionary[bow_doc_x[i][0]], 
                                                     bow_doc_x[i][1]))

lda_model =  gensim.models.LdaMulticore(bow_corpus, 
                                   num_topics = 30, 
                                   id2word = dictionary,                                    
                                   passes = 10,
                                   workers = 2)

'''
For each topic, we will explore the words occuring in that topic and its relative weight
'''
for idx, topic in lda_model.print_topics(-1):
    print("Topic: {} \nWords: {}".format(idx, topic ))
    print("\n")

from pandas import DataFrame
unseen_document = [""" India's states should declare an epidemic following a rise in deadly "black fungus" cases, the country's health authorities has said.

The normally rare infection, called mucormycosis, has a mortality rate of 50%, with some only saved by removing an eye or jaw bone.

But in recent months, India saw thousands of cases affecting recovered and recovering Covid-19 patients.

Doctors suspect there may be a link with the steroids used to treat Covid.

Diabetics are at particular risk, with doctors telling the BBC it seems to strike 12 to 15 days after recovery from Covid.

The deadly 'black fungus' maiming Covid patients
India's holiest river is swollen with bodies
Six hospitals, three days and a Covid nightmare
On Thursday, Health Ministry Joint Secretary Lav Agarwal wrote to India's 29 states to ask them to declare it an epidemic.

By doing so, the ministry will be able more closely to monitor what is happening in each state, and allow for better integration of treatment.

It is not clear exactly how many cases there have been across the country, which is currently in the grip of a deadly second Covid-19 wave which has left tens of thousands dead.  """]

df = DataFrame(unseen_document,columns=['text'])
docs = df['text']
docs=clean_data(docs)

def token(values):
    filtered_words = [word for word in values.split() if word not in stop_word_list]
    
    not_stopword_doc = " ".join(filtered_words)
    return not_stopword_doc
docs = docs.map(lambda x: token(x))
df = docs

bow_vector = dictionary.doc2bow(preprocess(df[0]))

# Data preprocessing step for the unseen document
count=0
for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1]):
    count+=1
    if(count<6):
      print("Score: %{}\t Topic: {}".format(score*100, re. findall('"([^"]*)"', lda_model.print_topic(index, 10))))