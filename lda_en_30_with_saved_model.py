# -*- coding: utf-8 -*-
"""LDA Wiki 70 (With Saved Model).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VMwG7TOaRj7OaX18nlV0aLQqa02x1u0G
"""

class result:
    """
    holds topic names and their proportions
    """"
    def __init__(self, topic, score):
        self.topic = topic
        self.score = score


def lda(thetext):
    """
    Main function to be called in interface
    """
    #!pip install gensim
    import gensim
    from gensim.utils import simple_preprocess
    import spacy
    #!pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.0/en_core_web_sm-2.2.0.tar.gz
    import pandas as pd
    import re
    import pickle
    import pandas as pd
    from nltk.stem.snowball import SnowballStemmer
    import nltk
    stemmer=SnowballStemmer('english')
    nltk.download('stopwords')
    WPT = nltk.WordPunctTokenizer()
    """Loading Prepared Model"""
    dictionary = gensim.corpora.Dictionary.load('Algorithm/NLP LDA EN 30 Topics/lda_eng_dictionary.gensim')
    corpus = pickle.load(open('Algorithm/NLP LDA EN 30 Topics/lda_eng_corpus.pkl', 'rb'))
    lda = gensim.models.ldamodel.LdaModel.load('Algorithm/NLP LDA EN 30 Topics/lda_eng_model.gensim')
    stop_word_list = nltk.corpus.stopwords.words('english')


    def lemmatize_stemming(text):
        """
        Stemming the words and returning
        """
        return stemmer.stem(text)

    def preprocess(text):
        """
        Filters the words according to stopwords and their length.
        """
        result=[]
        for token in gensim.utils.simple_preprocess(text) :
            if token not in stop_word_list and len(token) > 3:
                result.append(lemmatize_stemming(token))
        
        return result

    """Loading Unseen Document"""
    unseen_document = [thetext]
    """"Data Cleaning"""
    df = pd.DataFrame(unseen_document,columns=['text'])
    docs = df['text']
    docs = docs.map(lambda x: re.sub('[,\.\'!?();:$%&#"]', ' ', x))
    docs = docs.map(lambda x: x.lower())
    docs = docs.map(lambda x: x.strip())
    def token(values):
        filtered_words = [word for word in values.split() if word not in stop_word_list]
        
        not_stopword_doc = " ".join(filtered_words)
        return not_stopword_doc
    docs = docs.map(lambda x: token(x))
    df = docs

    data=[]
    data.append(preprocess(df[0]))

    bigram = gensim.models.Phrases(data, min_count=5, threshold=100)
    trigram = gensim.models.Phrases(bigram[data], threshold=100)  

    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram_mod = gensim.models.phrases.Phraser(trigram)



    def make_bigrams(texts):
        """
        Returns biagram of words
        """
        return [bigram_mod[doc] for doc in texts]

    def make_trigrams(texts):
        """
        Returns triagram of words
        """
        return [trigram_mod[bigram_mod[doc]] for doc in texts]

    def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        """
        Checks each word, make them lemmatized and returns lemmatized words as strings. Also only returns Nouns Adjectives Verbs and Adverbs
        """
        texts_out = []
        for sent in texts:
            doc = nlp(" ".join(sent)) 
            texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
        return texts_out

    data_words_trigrams = make_trigrams(data)

    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])


    data_lemmatized = lemmatization(data_words_trigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

    bow_vector = dictionary.doc2bow(data_lemmatized[0])
    topics = []
    count=0
    for index, score in sorted(lda[bow_vector], key=lambda tup: -1*tup[1]):
        count+=1
        if(count<6):
            print("Score: %{}\t Topic: {}".format(score*100, re. findall('"([^"]*)"', lda.print_topic(index, 10))))
            rslt = result(str(score), str(re.findall('"([^"]*)"', str(lda.print_topic(index,5)))))
            topics.append(rslt)
    
    return topics


if __name__ == '__main__':
    a = lda("this is a simple text to be analyzed.")
    for value in a:
        print(value.score)
        print(value.topic)
