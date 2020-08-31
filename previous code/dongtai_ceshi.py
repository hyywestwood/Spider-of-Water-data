# -*- coding: utf-8 -*-
# @Time    : 2019/4/24 19:33
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : dongtai_ceshi.py
# @Software: PyCharm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import os
import time
import random


# def get_data(url):
#     driver = webdriver.Firefox()
#     driver.get(url)
#     html = driver.page_source
#     bf = BeautifulSoup(html, 'html.parser')
#     data = bf.find_all('tr')
#     driver.close()
#     return data
def login_cc98():
    print('爬虫开始运行')
    url = 'https://www.cc98.org/logOn'
    driver = webdriver.Firefox()
    driver.get(url)

    # 等待至页面加载完成（loginName被加载出来）,否则10秒后报错
    element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'loginName')))

    elem = driver.find_element_by_name('username')
    elem.clear()
    elem.send_keys('会飞的豫')
    elem = driver.find_element_by_name('password')
    elem.clear()
    elem.send_keys('5896westwood')
    time.sleep(5)
    driver.find_element_by_xpath('//button').click()
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'mainPageListContent1')))
    html = driver.page_source
    driver.close()

    return html


if __name__ == '__main__':
    html = login_cc98()


