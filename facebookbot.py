#!/usr/bin/env python

import re
import requests
import xlwt
from os import getcwd as cwd
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from gooey import Gooey

class FaceBookBot:
    """Docstring for FaceBookBot. """
    def __init__(self, args):
        """TODO: to be defined1. """
        self._video_regex = r'.[a-zA-Z0-9]+.videos.[0-9]+.'
        self._args = args

    def setup_proxy(self, proxy):
        if proxy is None:
            return None
        return {'http': f'http://{proxy}', 'https': f'https://{proxy}'}

    def debug_print(self, string):
        if self._args.debug is True:
            print(f"[D] {string}")

    def get_req(self, url, proxy=None):
        '''
        custom self.get_req method
        '''
        print(f"Fetching -> {url}")
        r = requests.get(url, proxies=self.setup_proxy(proxy))
        if r.status_code == 200:
            return r
        print(f"Error fetching url -> {r}")

    def get_video_page(self, url):
        '''URL: https://www.facebook.com/goalcast/ -> https://www.facebook.com/pg/goalcast/videos/
        :return: request object of modified URL
        '''
        if 'videos' not in url:
            old_url = url
            url = f"{url}".replace("facebook.com/", "facebook.com/pg/")
            url = f"{url}videos/"
            self.debug_print(f'Converted Url {old_url} -> {url}')
        r = self.get_req(url)
        return r

    def get_video_links_array(self, r):
        '''
        :param: request object from get_video_page(url)
        :return: array of all video links on video page
        '''
        # Grabs all avaliable video links on a facebook page
        self.debug_print("Scraping Video Links")
        array = re.findall(self._video_regex, r.text)
        for n, i in enumerate(array):
            array[n] = f"https://facebook.com{i}"
            self.debug_print(f"Found {len(array)} Video Links")
        return list(set(array))

    def get_video_title(self, url, proxy=None):
        '''
        :param: URL of a direct video
        :return: 
        '''
        r = self.get_req(url, proxy=self.setup_proxy(proxy))
        return BeautifulSoup(r.content, 'html.parser').find('title').string

def open_file(filename):
    '''
    gets all the links from a textfile
    '''
    with open(filename) as f:
        return f.readlines()

def create_spreadsheet():
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet("Sheet 1")
    sheet.write(0, 0, "Title")
    sheet.write(0, 1, "Link")
    return book, sheet

def append_to_spreadsheet(title, link, sheet, y):
    sheet.write(y, 0, title)
    sheet.write(y, 1, link)

def write_spreadsheet(book, filename='results.xls'):
    book.save(filename)
    print(f'[+] Created spreadsheet {filename}')


@Gooey
def Main():
    parser = ArgumentParser()
    parser.add_argument('-f', '--filename', type=str, default=f'{cwd()}/links.txt', help='filename containing links of facebook page urls')
    args = parser.parse_args()
    bot = FaceBookBot(args)
    urls = open_file(args.filename)
    data = []
    for url in urls:
        video_page = bot.get_video_page(url)
        video_links_array = bot.get_video_links_array(video_page)
        for link in video_links_array:
            title = bot.get_video_title(link)
            data.append((title, link))
    book, sheet = create_spreadsheet()
    for i, n in enumerate(data):
        title = i[0]
        link = i[1]
        append_to_spreadsheet(title, link, sheet, n + 1)
    write_spreadsheet(book)
    print('[+] Complete')
    raise SystemExit(0)


if __name__ == '__main__':
    Main()

