#-*- coding: utf-8 -*-
"""
Author: DHSong
Date: 2020-06-26 (Last Modified)
Objective: EDA. 
"""

import pandas as pd
from konlpy.tag import Komoran
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pyLDAvis
from pyLDAvis.sklearn import prepare

class TopicModeling:
    """Topic Modeling with Visualization.

    Args:
        fpath (str): path to load dataset
    Return:
    """
    def __init__(self, fpath):
        self.dataframe = pd.read_csv(fpath, encoding='utf-8')  
        self.komoran = Komoran(userdic='./data/user_dic.tsv')

    def topic_modeling(self, n):
        """Topic Modeling using LDA in scikit-learn.

        Args:
            n (int): number of topic
        Return:
        """
        corpus = list()
        for idx in range(len(self.dataframe)):
            abstract = self.dataframe.loc[idx, 'abstract']
            nouns = [noun for noun in self.komoran.nouns(abstract) if len(noun) > 1]
            corpus.append(' '.join(nouns))

        tfidf = TfidfVectorizer(lowercase=False, min_df=10)
        doc2vec = tfidf.fit_transform(corpus)

        lda = LatentDirichletAllocation(n_components=n, verbose=True, random_state=2020)
        lda.fit(doc2vec)

        return lda, doc2vec, tfidf

    def visualize_lda(self, n):
        """Visualizing Topic Modeling using pyLDAvis.

        Args:
            n (int): number of topic
        Return:
        """
        lda, doc2vec, tfidf = self.topic_modeling(n)
        prepared = prepare(lda, doc2vec, tfidf)  
        pyLDAvis.save_html(prepared, './figure/topic_modeling.html')


if __name__ == '__main__':
    modeling = TopicModeling(fpath='./data/keyword-abstract.csv')
    modeling.visualize_lda(11)
                


