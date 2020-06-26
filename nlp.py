#-*- coding: utf-8 -*-
"""
Author: DHSong
Date: 2020-06-26 (Last Modified)
Objective: EDA. 
"""

from ast import literal_eval
from collections import Counter
import pandas as pd
from wordcloud import WordCloud
from konlpy.tag import Komoran
from tqdm import tqdm

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import seaborn as sns

class ArticleNLP:
    """ Basic Natural Language Processing. 
        Simple POS included by koNLPy

    Args:
        fpath (str): local path to load dataset
    Return:
    """
    def __init__(self, fpath):
        self.dataframe = pd.read_csv(fpath, encoding='utf-8')
        self.dataframe.keyword = self.dataframe.keyword.apply(literal_eval)

        plt.style.use('seaborn-darkgrid')

        font_name = './static/fonts/AppleSDGothicNeo.ttc'
        font_family = fm.FontProperties(fname=font_name).get_name()

        plt.rcParams['font.family'] = font_family
        plt.rcParams['font.size'] = 18

        self.komoran = Komoran(userdic='./data/user_dic.tsv')

    
    def count_keyword(self):
        """ Count number of keyword using collections.Counter

        Args:
        Return:
            counter (Counter): counter for keywords
        """
        keywords = list()
        for keyword in self.dataframe.keyword:
            keywords += keyword

        counter = Counter(keywords)        

        return counter

    def keyword_barplot(self, n=-1):
        """ Draw Barplot based on frequency of keyword. Save to local.

        Args:
            n (int): number of most frequent keywords to be plotted.
        Return:
        """
        counter = self.count_keyword()
        if n != -1:
            keyword_freq = dict(counter.most_common(n))
        else:
            keyword_freq = dict(counter.most_common())

        plt.figure(figsize=(16, 9))
        sns.barplot(x=list(keyword_freq.keys()), y=list(keyword_freq.values()))
        plt.xticks([])
        plt.xlabel('Keyword')
        plt.ylabel('Keyword Frequency')
        plt.title('Frequency of Keyword Distribution({})'.format(n if n != -1 else 'ALL'))
        plt.savefig('./figure/keyword_barplot.png')

    def keyword_wordcloud(self, n):
        """ Draw wordcloud based on frequency of keyword. Save to local.

        Args:
            n (int): number of most frequent keywords to be plotted.
        Return:
        """
        counter = self.count_keyword()

        plt.figure(figsize=(12, 12))
        wc = WordCloud(font_path='./static/fonts/NanumGothic.ttf', width=800, height=800, random_state=2020, background_color='white')
        wc.generate_from_frequencies(dict(counter.most_common(n)))
        plt.imshow(wc)
        plt.xticks([])
        plt.yticks([])
        plt.title('WordCloud of top 100 keywords')
        plt.tight_layout()
        plt.savefig('./figure/keyword_wordcloud.png')
    
    def keyword_year(self, n):
        """ Draw heatmap based on frequency of keyword among years. Save to local.

        Args:
            n (int): number of most frequent keywords to be plotted.
        Return:
        """
        counter = self.count_keyword()
        keywords = [k for k, _ in counter.most_common(n)]

        years = range(self.dataframe.year.min(), self.dataframe.year.max() + 1)
        df = pd.DataFrame(index=keywords, columns=years)
        df = df.fillna(0)

        for idx in tqdm(range(len(self.dataframe))):
            y = self.dataframe.loc[idx, 'year']
            ks = self.dataframe.loc[idx, 'keyword']
            for k in ks:
                if k in keywords:
                    df.loc[k, y] = df.loc[k, y] + 1
        
        plt.figure(figsize=(20, 32))
        sns.heatmap(df, annot=True)
        plt.title('Top {} Keywords occur in Each Year.'.format(n))
        plt.savefig('./figure/keyword_year.png')

    def keyword_cooccurence(self, n):
        """ Draw heatmap based on frequency of keyword cooccurence. Save to local.

        Args:
            n (int): number of most frequent keywords to be plotted.
        Return:
        """
        counter = self.count_keyword()
        keywords = [k for k, _ in counter.most_common(n)]

        df = pd.DataFrame(index=keywords, columns=keywords)
        df = df.fillna(0)

        for idx in tqdm(range(len(self.dataframe))):
            ks = self.dataframe.loc[idx, 'keyword']
            for src in ks:
                for dst in ks:
                    if src in keywords and dst in keywords:
                        df.loc[src, dst] = df.loc[src, dst] + 1
        
        plt.figure(figsize=(32, 32))
        sns.heatmap(df, annot=True)
        plt.title('Top {} Keywords Cooccurence'.format(n))
        plt.savefig('./figure/keyword_cooccurence.png')

    def count_abstract(self):
        """ Count number of noun in abstract using collections.Counter
            KoNLPy to extract nouns

        Args:
        Return:
            counter (Counter): counter for nouns
        """
        nouns = list()
        for abstract in self.dataframe.abstract:
            for n in self.komoran.nouns(abstract):
                nouns.append(n) if len(n) > 1 else None
        
        counter = Counter(nouns)
        return counter 

    def abstract_wordcloud(self, n):
        """ Draw wordcloud based on frequency of noun in abstract. Save to local.

        Args:
            n (int): number of most frequent nouns in abstract to be plotted.
        Return:
        """
        counter = self.count_abstract()

        plt.figure(figsize=(12, 12))
        wc = WordCloud(font_path='./static/fonts/NanumGothic.ttf', width=800, height=800, random_state=2020, background_color='white')
        wc.generate_from_frequencies(dict(counter.most_common(n)))
        plt.imshow(wc)
        plt.xticks([])
        plt.yticks([])
        plt.title('WordCloud of top 100 nouns on abstrat')
        plt.tight_layout()
        plt.savefig('./figure/abstract_wordcloud.png')

    def abstract_year(self, n, keyword):
        """ Draw heatmap based on frequency of nouns or keywords in abstract among years. Save to local.

        Args:
            n (int): number of most frequent words to be plotted.
            keyword (bool): if True then use keyword else use nouns
        Return:
        """
        if keyword:
            counter = self.count_keyword()
        else:
            counter = self.count_abstract()

        words = [k for k, _ in counter.most_common(n)]

        years = range(self.dataframe.year.min(), self.dataframe.year.max() + 1)
        df = pd.DataFrame(index=words, columns=years)
        df = df.fillna(0)

        for idx in tqdm(range(len(self.dataframe))):
            y = self.dataframe.loc[idx, 'year']
            abstracts = self.dataframe.loc[idx, 'abstract']
            for noun in self.komoran.nouns(abstracts):
                if noun in words:
                    df.loc[noun, y] = df.loc[noun, y] + 1
        
        plt.figure(figsize=(20, 32))
        sns.heatmap(df, annot=True)
        plt.title('Top {} {} occur in Each Year.'.format(n, 'Keyword in Abstract' if keyword else 'Noun in Abstract'))
        plt.savefig('./figure/abstract_year_{}.png'.format('keyword' if keyword else 'noun'))

    def abstract_cooccurence(self, n, keyword):
        """ Draw heatmap based on frequency of nouns or keywords in abstract cooccurence. Save to local.

        Args:
            n (int): number of most frequent words to be plotted.
            keyword (bool): if True then use keyword else use nouns
        Return:
        """
        if keyword:
            counter = self.count_keyword()
        else:
            counter = self.count_abstract()

        words = [k for k, _ in counter.most_common(n)]
        
        df = pd.DataFrame(index=words, columns=words)
        df = df.fillna(0)

        for idx in tqdm(range(len(self.dataframe))):
            abstracts = self.dataframe.loc[idx, 'abstract']
            nouns = self.komoran.nouns(abstracts)
            for src in words:
                for dst in words:
                    if src in nouns and dst in nouns:
                        df.loc[src, dst] = df.loc[src, dst] + 1
        
        plt.figure(figsize=(32, 32))
        sns.heatmap(df, annot=True)
        plt.title('Top {} {} in Abstract Cooccurence'.format(n, 'Keyword' if keyword else 'Noun'))
        plt.savefig('./figure/abstract_cooccurence_{}.png'.format('keyword' if keyword else 'noun'))


if __name__ == '__main__':
    nlp = ArticleNLP('./data/keyword-abstract.csv')
    nlp.keyword_barplot()
    counter_keyword = nlp.count_keyword()
    print(dict(counter_keyword.most_common(100)))
    nlp.keyword_wordcloud(100)
    nlp.keyword_year(50)
    nlp.keyword_cooccurence(50)

    counter_abstract = nlp.count_abstract()
    print(dict(counter_abstract.most_common(100)))
    nlp.abstract_wordcloud(100)
    nlp.abstract_year(50, keyword=True)
    nlp.abstract_year(50, keyword=False)
    nlp.abstract_cooccurence(50, keyword=True)
    nlp.abstract_cooccurence(50, keyword=False)

