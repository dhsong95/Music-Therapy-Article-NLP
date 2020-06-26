#-*- coding: utf-8 -*-
"""
Author: DHSong
Date: 2020-06-22 (Last Modified)
Objective: EDA. 
"""

from ast import literal_eval

import pandas as pd

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import seaborn as sns

class EDA:
    """EDA for 한국음악치료학회지 Article from RISS.

    Args:
        fpath (str): local csv file path for EDA
    Return:
    """
    def __init__(self, fpath):
        self.dataframe = pd.read_csv(fpath, encoding='utf-8')

        # initializt matplotlib korean setting
        fname = './static/fonts/NanumGothic.ttf'
        ffamily = fm.FontProperties(fname=fname).get_name()
        plt.rcParams['font.family'] = ffamily
        plt.rcParams['font.size'] = 14

        plt.style.use('seaborn-darkgrid')

    def show_samples(self, n):
        """show sample of record

        Args:
            n (int): number of record to be shown
        Return:
            sample (pandas DataFrame): sample Dataframe
        """
        sample = self.dataframe.sample(n)
        return sample
    
    def select_columns(self, columns):
        """targeting column in dataframe. remove else.

        Args:
            columns (list): column to be selected
        Return:
        """
        self.dataframe = self.dataframe[columns]

    def remove_duplicates(self):
        """remove duplicated record (marked manually)

        Args:
        Return:
            n_duplicated (int): number of duplicated record
        """
        if 'is_duplicated' in self.dataframe.columns:
            n_duplicated = self.dataframe.is_duplicated.sum()
            self.dataframe = self.dataframe[~self.dataframe.is_duplicated]
            self.dataframe.drop(columns=['is_duplicated'], inplace=True)
            return n_duplicated
        else:
            return 0

    def remove_non_articles(self):
        """remove non article records (marked manually)

        Args:
        Return:
            n_non_article (int): number of non article
        """
        if 'non_article' in self.dataframe.columns:
            n_non_article = self.dataframe.non_article.sum()
            self.dataframe = self.dataframe[~self.dataframe.non_article]
            self.dataframe.drop(columns=['non_article'], inplace=True)
            return n_non_article
        else:
            return 0

    def remove_english_articles(self):
        """remove english article records (marked manually)

        Args:
        Return:
            n_english_article (int): number of non article
        """
        if 'language' in self.dataframe.columns:
            self.dataframe.language == 'English'
            n_english_article = len(self.dataframe[self.dataframe.language == 'English'])
            self.dataframe = self.dataframe[~(self.dataframe.language == 'English')]
            self.dataframe.drop(columns=['language'], inplace=True)
            return n_english_article
        else:
            return 0

    def remove_no_abstract_articles(self):
        """remove article without abstract

        Args:
        Return:
            n_no_abstract_article (int): number of non article
        """
        n_no_abstract_article = len(self.dataframe[self.dataframe.abstract == ''])
        self.dataframe = self.dataframe[~(self.dataframe.abstract == '')]
        return n_no_abstract_article

    def count_articles_language(self):
        """Visualize the frequency of article based on language

        Args:
        Return:
            language_freq (dict): language-frequency dictionary
        """
        self.dataframe.language = self.dataframe.language.fillna('-')

        language_counts = self.dataframe.language.value_counts().sort_index()

        plt.figure(figsize=(16, 9))
        sns.barplot(language_counts.index, language_counts.values)
        plt.xlabel('language')
        plt.ylabel('number of articles')
        plt.title('What Language do articles published in?')        
        plt.savefig('./figure/count_articles_language.png')

        language_freq = {language:freq for language, freq in language_counts.items()}
        return language_freq

    def count_articles_year(self):
        """Visualize the frequency of article based on year

        Args:
        Return:
            year_freq (dict): year-frequency dictionary
        """
        year_counts = self.dataframe.year.value_counts().sort_index()

        plt.figure(figsize=(16, 9))
        sns.lineplot(year_counts.index, year_counts.values)
        plt.xlabel('year')
        plt.ylabel('number of articles')
        plt.title('When do articles published?')        
        plt.savefig('./figure/count_articles_year.png')

        year_freq = {year:freq for year, freq in year_counts.items()}
        return year_freq

    def count_number_of_keyword(self):
        """Visualize the frequency of number of keyword per article

        Args:
        Return:
            n_keyword_freq (dict): number-frequency dictionary
        """
        self.dataframe.keyword = self.dataframe.keyword.fillna('[]')
        self.dataframe.keyword = self.dataframe.keyword.apply(literal_eval)
        self.dataframe['n_keyword'] = self.dataframe.keyword.apply(len)

        n_keyword_counts = self.dataframe.n_keyword.value_counts().sort_index()

        plt.figure(figsize=(16, 9))
        sns.lineplot(n_keyword_counts.index, n_keyword_counts.values)
        plt.xlabel('number of keyword')
        plt.ylabel('number of articles')
        plt.title('How many keywords are allocated to article?')        
        plt.savefig('./figure/count_number_of_keyword.png')

        n_keyword_freq = {n_keyword:freq for n_keyword, freq in n_keyword_counts.items()}
        return n_keyword_freq

    def count_length_of_abstract(self):
        """Visualize the frequency of number of word in abstract(length) per article

        Args:
        Return:
            len_abstract_freq (dict): number-frequency dictionary
        """
        self.dataframe.abstract = self.dataframe.abstract.fillna('')
        self.dataframe['len_abstract'] = self.dataframe.abstract.apply(lambda x: len(x.split()))

        len_abstract_counts = self.dataframe.len_abstract.value_counts().sort_index()

        plt.figure(figsize=(16, 9))
        sns.lineplot(x=len_abstract_counts.index, y=len_abstract_counts.values)
        plt.xlabel('number of articles')
        plt.ylabel('length of abstract(number of word in abstract)')
        plt.title('How mant words are in abstract per article?')        
        plt.savefig('./figure/count_length_of_abstract.png')

        len_abstract_freq = {len_abstract:freq for len_abstract, freq in len_abstract_counts.items()}
        return len_abstract_freq


    def save_data_for_nlp(self, fpath):
        """Save Data for NLP

        Args:
            fpath (str): Save path
        Return:
        """
        _ = self.remove_duplicates()
        _ = self.remove_non_articles()
        _ = self.remove_english_articles()
        _ = self.remove_no_abstract_articles()

        self.dataframe = self.dataframe[['title', 'year', 'keyword', 'abstract']]

        self.dataframe.to_csv(fpath, encoding='utf-8', index=False)


if __name__ == '__main__':
    eda = EDA(fpath='./data/article_filled.csv')
    print(eda.show_samples(10)) 

    eda.select_columns(['title', 'year', 'language', 'keyword', 'abstract', 'is_na_keyword', 'is_na_abstract', 'non_article', 'is_duplicated'])
    print(eda.show_samples(10)) 

    n = eda.remove_duplicates()
    print('{} duplicated record is removed'.format(n))

    n = eda.remove_non_articles()
    print('{} non article record is removed'.format(n))

    print(eda.count_articles_language())

    print(eda.count_articles_year())

    print(eda.count_number_of_keyword())

    print(eda.count_length_of_abstract())

    fpath = './data/keyword-abstract.csv'
    eda.save_data_for_nlp(fpath)
