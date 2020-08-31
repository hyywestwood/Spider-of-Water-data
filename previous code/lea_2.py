# -*- coding: utf-8 -*-
# @Time    : 2019/4/22 15:23
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : lea_2.py
# @Software: PyCharm
from urllib.request import urlopen
from bs4 import BeautifulSoup
html = urlopen("http://www.pythonscraping.com/pages/warandpeace.html")
bsObj = BeautifulSoup(html)
nameList = bsObj.findAll("span", {"class":"green"})
for name in nameList:
    print(name.get_text())