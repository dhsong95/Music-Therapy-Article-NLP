#-*- coding: utf-8 -*-
"""
Author: DHSong
Date: 2020-06-22 (Last Modified)
Objective: Cawling Article Data from RISS. 
"""

import pandas as pd

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

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
        n_duplicated = self.dataframe.is_duplicated.sum()
        self.dataframe = self.dataframe[~self.dataframe.is_duplicated]
        self.dataframe.drop(columns=['is_duplicated'], inplace=True)
        return n_duplicated

    def remove_non_articles(self):
        """remove non article records (marked manually)

        Args:
        Return:
            n_non_article (int): number of non article
        """
        n_non_article = self.dataframe.non_article.sum()
        self.dataframe = self.dataframe[~self.dataframe.non_article]
        self.dataframe.drop(columns=['non_article'], inplace=True)
        return n_non_article

    def articles_by_language(self):
        plt.figure(figsize=(16, 9))
        # plt.bar(self.dataframe.language.value_counts(drop=False).sort_index())
        plt.xlabel('language')
        plt.ylabel('number of articles')
        plt.title('articles published in language')        
        plt.savefig('./figure/article_by_language.png')

        language_freq = {year:freq for year, freq in self.dataframe.language.value_counts().sort_index().items()}
        return language_freq

    def articles_by_year(self):
        plt.figure(figsize=(16, 9))
        plt.plot(self.dataframe.year.value_counts().sort_index())
        plt.xlabel('year')
        plt.ylabel('number of articles')
        plt.title('articles published per year')        
        plt.savefig('./figure/article_by_year.png')

        year_freq = {year:freq for year, freq in self.dataframe.year.value_counts().sort_index().items()}
        return year_freq
       


if __name__ == '__main__':
    eda = EDA(fpath='./data/article_filled.csv')
    print(eda.show_samples(10)) 

    eda.select_columns(['title', 'year', 'language', 'keyword', 'is_na_keyword', 'is_na_abstract', 'non_article', 'is_duplicated'])
    print(eda.show_samples(10)) 

    n = eda.remove_duplicates()
    print('{} duplicated record is removed'.format(n))

    n = eda.remove_non_articles()
    print('{} non article record is removed'.format(n))

    n = eda.remove_english_articles()
    print('{} english article record is removed'.format(n))

    print(eda.articles_by_year())

