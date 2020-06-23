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

import pandas as pd


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

    def crawl_title_url(self, filename):
        '''Crawl Article Title and URL
        
        Args:
            filename (str): save path. 
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
        df.to_csv(filename, encoding='utf-8', index=False)

    def close(self):
        '''Close URL
        
        Args:
        Return:
        '''
        self.driver.close()


if __name__ == '__main__':
    driver_path = './driver/chromedriver'
    base_url = 'http://www.riss.kr/search/detail/DetailView.do?p_mat_type=3a11008f85f7c51d&control_no=2a75a048a6856c25ffe0bdc3ef48d419'
    crawler = CrawlingArticle(driver_path, base_url, False)

    crawler.open()
    time.sleep(0.5)

    filename = './data/title-url.csv'
    if not os.path.exists(filename):
        crawler.crawl_title_url(filename)
    time.sleep(0.5)

    
    crawler.close()

