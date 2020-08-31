# -*- coding: utf-8 -*-
# @Time    : 2019/6/4 16:17
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : data_of_changjiang.py
# @Software: PyCharm
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import time
import random
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_data(url):
    retry_count = 3

    while retry_count > 0:
        try:
            driver = webdriver.Firefox()
            time.sleep(15)
            driver.set_page_load_timeout(75)    #设置等待时间,保险起见，设为75秒
            driver.set_script_timeout(75)
            driver.get(url)
            element = WebDriverWait(driver, 15).until(EC.title_is('水情信息'))
            # print('网页动态内容加载完成')
            time.sleep(random.uniform(5, 20))   #在当前页面随机停留一段时间
            html = driver.page_source
            bf = BeautifulSoup(html, 'html.parser')
            data = bf.find_all('tr')
            driver.close()
            return data
        except Exception:
            print('错误发生，重新尝试获取，剩余次数{}'.format(retry_count-1))
            retry_count -= 1
            driver.close()
    return None


def trans(a):
    data = []
    for i in range(1,len(a)):
        zhandian = []
        for j in a[i].contents:
            # print(j.text)
            zhandian.append(j.text)
        data.append(zhandian)
    return data


def write_data(a, a_ex):
    # 对数据a,a_ex进行处理
    data = trans(a)
    data1 = trans(a_ex)

    dizhi = [x[0] for x in data1]   #记录已有地址和时间
    shijian = [x[1] for x in data1]
    # 使用列表解析读取二维列表的单独列  [x[0] for x in data]

    # 新爬取结果与旧数据对比，将更新的结果写入文件
    for hang in data:
        if dizhi.count(hang[0]) != 0:   #地址存在
            index = dizhi.index(hang[0])    #标记索引
            if hang[1] != shijian[index]:
                with open(path1 + '\\长江水文\\' + '{}.txt'.format(hang[0]),
                          'a',encoding='utf-8') as f:
                    f.write('{}\t{}\t{} \n'.format(time.strftime("%Y-%m", time.localtime()) + '月'  + hang[1],hang[2], hang[3]))
        else:
            # 当地址不存在时，创建新文件
            with open(path1 + '\\长江水文\\' + '{}.txt'.format(hang[0]),
                      'w', encoding='utf-8') as f:
                f.write('{}\t{}\t{} \n'.format('时间', '水位（米）', '流量（m^3/s）'))
    a_ex = a
    print('{}时间数据爬取完成'.format(time.strftime("%m-%d-%H", time.localtime())))
    now = datetime.datetime.now()
    sleep_time = 3600 + random.uniform(1, 10)
    end = now + datetime.timedelta(days=sleep_time / 86400)
    print('开始休眠，将休眠至：{}'.format(end))
    time.sleep(sleep_time)
    return a_ex


if __name__ == '__main__':
    path1 = os.path.abspath('.')  # 获取当前脚本所在的路径
    folder = os.path.exists(path1 + '\\长江水文')
    if not folder:
        os.makedirs(path1 + '\\长江水文')
    print('爬虫开始运行')
    url = 'http://www.cjh.com.cn/sqindex.html'
    a_ex = None
    while a_ex is None:
        a_ex = get_data(url)

    # 如程序不小心崩了，请将下面这小段代码注释再运行
    data = trans(a_ex)
    for hang in data:
        with open(path1 + '\\长江水文\\' + '{}.txt'.format(hang[0]),
                  'w', encoding='utf-8') as f:
            f.write('{}\t\t{}\t{} \n'.format('时间', '水位（米）', '流量（m^3/s）'))
            f.write('{}\t{}\t{} \n'.format(time.strftime("%Y-%m", time.localtime()) + '月' + hang[1], hang[2], hang[3]))


    # 主循环，保留
    while True:
        a = None
        while a is None:
            a = get_data(url)
        a_ex = write_data(a, a_ex)


