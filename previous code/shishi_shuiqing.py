# -*- coding: utf-8 -*-
# @Time    : 2019/4/24 19:33
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : dongtai_ceshi.py
# @Software: PyCharm
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import time
import random


def get_data(url):
    retry_count = 5
    proxy = get_proxy()
    profile = webdriver.FirefoxOptions()
    # profile.add_argument('-headless')  # 设置无头模式
    # 设置代理服务器
    IP, PORT = proxy.decode('utf-8').split(':')
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.http', IP)  # IP为你的代理服务器地址:如‘127.0.0.0’，字符串类型
    profile.set_preference('network.proxy.http_port', int(PORT))  # PORT为代理服务器端口号:如，9999，整数类型
    while retry_count > 0:
        try:
            driver = webdriver.Firefox(options=profile)
            driver.get(url)
            html = driver.page_source
            bf = BeautifulSoup(html, 'html.parser')
            data = bf.find_all('tr')
            driver.close()
            return data
        except Exception:
            retry_count -= 1
    delete_proxy(proxy)
    return None


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def write_data(a):
    for i in range(1, len(a)):
        d_str = a[i].text
        d_str = d_str.replace('↑', '')
        d_str = d_str.replace('↓', '')
        d_str = d_str.replace('—', '')
        d_str = d_str.replace('\xa0', '')
        d_str = d_str.rstrip()[1:len(d_str)]
        data = d_str.split('\n')
        with open(path1 + '\\大江大河实时水情\\' + data[0] + '\\' + '{}-{}-{}.txt'.format(data[1], data[2], data[3]), 'a',
                  encoding='utf-8') as f:
            f.write('{}\t{}\t{}\t{} \n'.format(data[4], data[5], data[6], data[7]))
    print('此时间爬取完成：', end='')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


if __name__ == '__main__':
    path1 = os.path.abspath('.')  # 获取当前脚本所在的路径
    folder = os.path.exists(path1 + '\\大江大河实时水情')
    if not folder:
        os.makedirs(path1 + '\\大江大河实时水情')
    print('爬虫开始运行')
    url = 'http://ditu.92cha.com/shuiqing.php?w=hd'
    # a = get_data(url)
    # for i in range(1,len(a)):
    #     d_str = a[i].text
    #     d_str = d_str.replace('↑', '')
    #     d_str = d_str.replace('↓', '')
    #     d_str = d_str.replace('—', '')
    #     d_str = d_str.replace('\xa0', '')
    #     d_str = d_str.rstrip()[1:len(d_str)]
    #     data = d_str.split('\n')
    #     folder = os.path.exists(path1 + '\\大江大河实时水情\\'+ data[0])
    #     if not folder:
    #         os.makedirs(path1 + '\\大江大河实时水情\\'+ data[0])
    #     with open(path1 + '\\大江大河实时水情\\'+ data[0] + '\\' + '{}-{}-{}.txt'.format(data[1],data[2],data[3]), 'w', encoding='utf-8') as f:
    #         f.write('{}\t{}\t{}\t{} \n'.format('时间', '水位（米）', '流量（m^3/s）', '警戒水位（米）'))
    #         f.write('{}\t{}\t{}\t{} \n'.format(data[4], data[5], data[6], data[7]))
    # print('初始数据爬取完成')
    while True:
        print('sleep now')
        time.sleep(random.uniform(1,8))
        a = get_data(url)
        write_data(a)


