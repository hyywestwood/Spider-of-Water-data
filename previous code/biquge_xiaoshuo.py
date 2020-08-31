# -*- coding: utf-8 -*-
# @Time    : 2019/4/21 15:17
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : biquge_xiaoshuo.py
# @Software: PyCharm
import os
from bs4 import BeautifulSoup
import requests
import time
import random


def down_phrase(url):
    req = requests.get(url=url)
    html = req.text
    bf = BeautifulSoup(html, 'html.parser')
    title = bf.find('div', class_='content').h1.contents[0]
    texts = bf.find('div', id='content', class_='showtxt').text
    texts = texts.replace('\xa0' * 8, '\n\n')
    next_page = bf.find_all('div', class_='page_chapter')[0]
    next_page = BeautifulSoup(str(next_page), 'html.parser')
    next_page = next_page.find_all('a')[2].get('href')
    return texts, title, next_page


def write_file(name, text):
    with open(path1+ '\\笔趣阁—一念永恒\\' + name + '.txt', 'w', encoding='utf-8') as f:
        f.writelines(text)


if __name__ == '__main__':
    path1 = os.path.abspath('.')  # 获取当前脚本所在的路径
    folder = os.path.exists(path1 + '\\笔趣阁—一念永恒')
    if not folder:
        os.makedirs(path1 + '\\笔趣阁—一念永恒')
    target = 'https://www.biqukan.com'
    str1 = '/1_1094/6319943.html'
    k = 1
    while True:
        text, name, str1 = down_phrase(target+str1)
        write_file(name,text)
        time.sleep(random.uniform(100,200))
        if k % 10 == 0:
            time.sleep(2*60)
        if k % 50 == 0:
            time.sleep(6*60)
        print('已完成： ' + name)
        k = k+1

