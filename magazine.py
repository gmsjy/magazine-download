# coding:utf-8

"""
GetPDF

Usage:
magazine.py  <magazine> <date>

Options:
    -h, --help 显示帮助
    

Example:
    magazine.py [z|g|j] 2017110201
    magazine 参数: j 解放军报
          g 中国国防报

"""

import os
import re
import time
import datetime
import logging
import requests
import redis
import peewee
from bs4 import BeautifulSoup
from docopt import docopt

'''
Logging 模块基本    设置
'''
logger = logging.getLogger('MagazineDownload')

formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

file_handler = logging.FileHandler('magazinelogger.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.setLevel(logging.INFO)

'''
DataBase 设置
'''

db = peewee.SqliteDatabase('magazine.db')


class NewsModel(peewee.Model):
    category = peewee.CharField()
    date = peewee.DateField()
    section = peewee.IntegerField()
    title = peewee.CharField()
    author = peewee.CharField()

    class Meta:
        database = db


class Magazine():
    """ 作为杂志爬虫基类 """

    def __init__(self, keywords):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'Keep-Alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        }
        self.keywords = keywords
        self.urls = []
        self.filenames = []
        self.get_filename()
        self.get_url()

    def get_filename(self):
        return ""

    def get_url(self):
        pass

    def get_pdf(self):
        TimeFormat = "%a %b %d %H:%M:%S %Y"
        print(self.urls, self.filenames)
        if not os.path.exists(os.path.dirname(self.filenames[0])):
            os.mkdir(os.path.dirname(self.filenames[0]))
        for url, filename in zip(self.urls, self.filenames):
            try:
                print("linking..................!!!!!")
                content = requests.get(url)
            except Exception as e:
                logging.info(e)
                return None
            if content.status_code == 200:
                print("linked!!!!!")
                with open(filename, "wb") as f:
                    f.write(content.content)
                    print(filename, 'Write file successed.....')
                    logger.info("=========" + datetime.datetime.today().strftime(TimeFormat) +
                                "=========  " + self.get_filename() + "  successed!")


class PlaMagazine(Magazine):
    """ PLA 杂志 """

    def get_url(self):
        """ keys is string .
        For example:
        keys = "2017112701"
        """
        self.urls = []
        keys = self.keywords
        url = 'http://www.81.cn/jfjbmap/content/1/{Year}-{Month}/{Day}/{Section}/{Year}{Month}{Day}{Section}_pdf.pdf'.format(Year=keys[0:4], Month=keys[4:6], Day=keys[6:8],
                                                                                                                             Section=keys[8:10])
        self.urls.append(url)

    def get_filename(self):
        """
        Get the filename
        """
        keys = self.keywords
        filename = os.path.join(os.getcwd(), "PLA", keys + ".pdf")
        self.filenames.append(filename)
        return filename


class GfbMagazine(Magazine):
    """ 国防报杂志 """

    def get_url(self):
        """ keys is string .
        For example:
        keys = "2017112701"
        """
        self.urls = []
        keys = self.keywords
        url = 'http://www.81.cn/gfbmap/content/21/{Year}-{Month}/{Day}/{Section}/{Year}{Month}{Day}{Section}_pdf.pdf'.format(Year=keys[0:4], Month=keys[4:6], Day=keys[6:8],
                                                                                                                             Section=keys[8:10])
        self.urls.append(url)
        return url

    def get_filename(self):
        """
        Get the filename
        """
        keys = self.keywords
        filename = os.path.join(os.getcwd(), "GFB", keys + ".pdf")
        self.filenames.append(filename)
        return filename


magazine_map = {
    'j': PlaMagazine,
    'g': GfbMagazine
}


def cli():
    arguments = docopt(__doc__)
    magazine = arguments['<magazine>']
    newsdate = arguments['<date>']
    if newsdate[8:10] != '01':
        download = magazine_map[magazine](newsdate[0:8] + '01')
        print(download.get_url())
        download.get_pdf()

    download = magazine_map[magazine](newsdate)
    print(download.get_url())
    download.get_pdf()


if __name__ == "__main__":
    cli()
