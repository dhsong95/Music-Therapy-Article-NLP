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


class CrawlingArticle:
    """Crawling 한국음악치료학회지 Article from RISS.

    Args:
        driver_path (str): local driver path
        base_url (str): 한국음악치료학회지 RISS URL
        headless (boolean): whether driver works in headless
    Return:
    """
    def __init__(self, driver_path, base_url, headless=True):
        options = webdriver.ChromeOptions()
        if headless:    
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument('disable-gpu')
        self.driver = webdriver.Chrome(driver_path, options=options)
        self.base_url = base_url


    def open(self, url=None):
        '''Open URL
        
        Args:
            url (str): url to be opened. 
        Return:
        '''
        if url is not None:
            self.driver.get(url)
        else:
            self.driver.get(self.base_url)


    def crawl_title_url(self, save_fpath):
        '''Crawl Article Title and URL. Save to $save_fpath in csv format
        
        Args:
            save_fpath (str): save path. 
        Return:
        '''
        titles = list()
        urls = list()

        year_elements = self.driver.find_elements_by_xpath('//*[@id="divContent"]/div[1]/div/div[2]/ul/li')
        for idx in range(len(year_elements)):
            self.driver.execute_script(
                'arguments[0].click();', 
                self.driver.find_element_by_xpath('//*[@id="divContent"]/div[1]/div/div[2]/ul/li[{}]/a'.format(idx + 1))
            )
            time.sleep(1)

            no_elements = self.driver.find_elements_by_xpath('//*[@id="divContent"]/div[1]/div/div[2]/ul/li[{}]/ul/li'.format(idx + 1))
            for jdx in range(len(no_elements)):
                self.driver.execute_script(
                    'arguments[0].click();', 
                    self.driver.find_element_by_xpath('//*[@id="divContent"]/div[1]/div/div[2]/ul/li[{}]/ul/li[{}]/a'.format(idx + 1, jdx + 1))
                )
                time.sleep(3)

                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                elements = soup.select('#soptionview > div > div.srchResultW.bd.bd2 > div.srchResultListW > ul > li')
                for element in elements:
                    title = element.find('div', 'cont').find('p', 'title').get_text().strip()
                    url = element.find('div', 'cont').find('p', 'title').find('a')['href']
                    print('{:s}\t{:s}'.format(title, url))
                    titles.append(title)
                    urls.append(url)
        
        df = pd.DataFrame(columns=['title', 'url'])
        df['title'] = titles
        df['url'] = urls
        df.to_csv(save_fpath, encoding='utf-8', index=False)


    def crawl_article(self, load_fpath, save_fpath, verbose=False):
        '''Crawl Article Information. Save to $save_fpath in csv format
        
        Args:
            load_fpath (str): path to load artitle-url. 
            save_fpath (str): save path. 
            verbose (boolean): whether to show data while progressing. Default Fasle. 
        Return:
        '''
        title_url_df = pd.read_csv(load_fpath, encoding='utf-8')

        article_dict = {
            'title': list(), 'author': list(), 'organization': list(), 'name': list(), 'volno': list(), 'year': list(), 
            'language': list(), 'keyword': list(), 'kdc': list(), 'kci': list(), 'media': list(), 'page': list(), 
            'citation': list(), 'link': list(), 'abstract': list(), 'location': list()
        }

        for idx in tqdm(range(len(title_url_df))):
            title = title_url_df.loc[idx, 'title']
            url = title_url_df.loc[idx, 'url']
            url = 'http://www.riss.kr' + url
            self.open(url)
            time.sleep(3)
    
            mores = self.driver.find_elements_by_class_name('moreView')
            for more in mores:
                self.driver.execute_script('arguments[0].click();', more)
                time.sleep(1)
            time.sleep(1)

            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
    
            author = np.nan
            org = '한국음악치료학회'
            name = '한국음악치료학회지'
            volno = np.nan
            year = np.nan
            lang = np.nan
            keyword = np.nan
            kdc = np.nan
            kci = np.nan
            media = '학술저널'
            page = np.nan
            citation = np.nan
            link = np.nan
            abstract = np.nan
            loc = np.nan
    
            elements = soup.select('#soptionview > div > div.thesisInfo > div.infoDetail > div.infoDetailL > ul > li')
            for element in elements:
                key = element.find('span', 'strong').get_text().strip()
                value = element.find('div').get_text().strip()
                
                if key == '저자':
                    author = value
                elif key == '발행기관':
                    org = value
                elif key == '학술지명':
                    name = value
                elif key == '권호사항':
                    volno = ' '.join(value.split())
                elif key == '발행연도':
                    year = value
                elif key == '작성언어':
                    lang = value
                elif key == '주제어':
                    keyword = ' '.join(value.split())
                elif key == 'KDC':
                    kdc = value
                elif key == '등재정보':
                    kci = value
                elif key == '자료형태':
                    media = value
                elif key == '수록면':
                    page = value
                elif key == 'KCI 피인용지수' or key == 'KCI 피인용횟수':
                    citation = value
                elif key == '제공처':
                    link = value
                elif key == '소장기관':
                    loc = value
                else:
                    print('*********New Key: {:s}*********'.format(key))

            additionals = soup.find_all('div', 'innerCont')
            for addition in additionals:
                if addition.find('h3', 'tit').get_text().strip() == '부가정보':
                    contents = addition.select('div.content > div')
                    for content in contents:
                        if content.find('p', 'title').get_text().strip() == '국문 초록 (Abstract)':
                            abstract = content.find_all('div', 'text')[1].find('p').get_text().strip()
                            break
            
            if verbose:
                print('{:s}\t{:s}\t{:s}\n\t{:s}'.format(title, volno, keyword, abstract))
    
            article_dict['title'].append(title)
            article_dict['author'].append(author)
            article_dict['organization'].append(org)
            article_dict['name'].append(name)
            article_dict['volno'].append(volno)
            article_dict['year'].append(year)
            article_dict['language'].append(lang)
            article_dict['keyword'].append(keyword)
            article_dict['kdc'].append(kdc)
            article_dict['kci'].append(kci)
            article_dict['media'].append(media)
            article_dict['page'].append(page)
            article_dict['citation'].append(citation)
            article_dict['link'].append(link)
            article_dict['abstract'].append(abstract)  
            article_dict['location'].append(loc)  

        article_df = pd.DataFrame(article_dict)
        article_df.to_csv(save_fpath, encoding='utf-8', index=False)


    def close(self):
        '''Close URL
        
        Args:
        Return:
        '''
        self.driver.close()


if __name__ == '__main__':
    driver_path = './driver/chromedriver'
    base_url = 'http://www.riss.kr/search/detail/DetailView.do?p_mat_type=3a11008f85f7c51d&control_no=2a75a048a6856c25ffe0bdc3ef48d419'
    crawler = CrawlingArticle(driver_path, base_url, True)

    crawler.open()
    time.sleep(0.5)

    save_fpath = './data/title-url.csv'
    if not os.path.exists(save_fpath):
        crawler.crawl_title_url(save_fpath)
    time.sleep(0.5)

    load_fpath = save_fpath
    save_fpath = './data/article.csv'
    if not os.path.exists(save_fpath):
        crawler.crawl_article(load_fpath, save_fpath)
    time.sleep(0.5)

    crawler.close()

