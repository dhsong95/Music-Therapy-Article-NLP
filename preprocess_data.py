#-*- coding: utf-8 -*-
"""
Author: DHSong
Date: 2020-06-22 (Last Modified)
Objective: Cawling Article Data from RISS. 
"""

import time
import re
import os

from bs4 import BeautifulSoup
from selenium import webdriver

import numpy as np
import pandas as pd

from tqdm import tqdm


class PreprocessingArticle:
    """Preprocessing 한국음악치료학회지 Article crawled from RISS.

    Args:
        fpath (str): CSV path of crawled data
    Return:
    """
    def __init__(self, fpath):
        self.dataframe = pd.read_csv(fpath, encoding='utf-8')

    def sample_item(self, column, n):
        """Sampling record in dataframe

        Args:
            column (str): what column to be extracted
            n (int): numbers to be sampled
        Return:
            sample (Pandas Series): Sampled Dataframe
        """
        assert column in self.dataframe.columns

        sample = self.dataframe[column].sample(n=n)
        return sample

    def preprocess_author(self):
        """Author has unnecessarity white spaces(\t\n ). remove and make list of authors.

        Args:
        Return:
        """
        self.dataframe['author'] = self.dataframe.author.str.replace(r'[ \n\t][ \n\t]+', '')
        self.dataframe['author'] = self.dataframe.author.str.replace(', ', ' ')
        self.dataframe['author'] = self.dataframe.author.str.split(',')

    def preprocess_volno(self):
        """Split volumne and no.

        Args:
        Return:
        """
        self.dataframe['vol'] = self.dataframe.volno.str.extract(r'(?:Vol.)([\d]+)')
        self.dataframe['no'] = self.dataframe.volno.str.extract(r'(?:No.)([\d]+)')

    def preprocess_keyword(self):
        """Split keyword to make list.

        Args:
        Return:
        """
        self.dataframe['keyword'] = self.dataframe.keyword.str.strip()
        self.dataframe['author'] = self.dataframe.author.str.replace(r'[ \n\t][ \n\t]+', ' ')
        self.dataframe['keyword'] = self.dataframe.keyword.str.split(' , ')
    
    def preprocess_page(self):
        """Split page into start page and end page.

        Args:
        Return:
        """
        self.dataframe['page_start'] = self.dataframe.page.str.extract(r'([\d]+)(?:-)')
        self.dataframe['page_end'] = self.dataframe.page.str.extract(r'(?:-)([\d]+)')

    def preprocess_abstract(self):
        """Remove White Space in abstract

        Args:
        Return:
        """
        self.dataframe['abstract'] = self.dataframe.abstract.str.strip()
        self.dataframe['abstract'] = self.dataframe.abstract.str.replace(r'[ \n\t][ \n\t]+', ' ')

    def save(self, fpath):
        """Save Dataframe Processed.

        Args:
            fpath (str): path to save dataframe as CSV
        Return:
        """
        self.dataframe.to_csv(fpath, encoding='utf-8', index=False)

if __name__ == '__main__':
    fpath = './data/article_raw.csv'
    preprocessor = PreprocessingArticle(fpath)
    
    preprocessor.preprocess_author()
    print(preprocessor.sample_item('author', 10))

    preprocessor.preprocess_volno()
    print(preprocessor.sample_item('vol', 10))
    print(preprocessor.sample_item('no', 10))

    preprocessor.preprocess_keyword()
    print(preprocessor.sample_item('keyword', 10))

    preprocessor.preprocess_page()
    print(preprocessor.sample_item('page_start', 10))
    print(preprocessor.sample_item('page_end', 10))

    preprocessor.preprocess_abstract()
    print(preprocessor.sample_item('abstract', 10))

    fpath = './data/article.csv'
    preprocessor.save(fpath)



