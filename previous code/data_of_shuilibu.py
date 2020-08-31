# -*- coding: utf-8 -*-
# @Time    : 2019/6/20 20:20
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : data_of_shuilibu.py
# @Software: PyCharm
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import time
import random
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def get_data(url):
    retry_count = 3
    proxy = get_proxy()
    # 设置代理服务器
    try:
        IP, PORT = proxy.decode('utf-8').split(':')
    except Exception:
        print('可用代理为空，等待5分钟')
        time.sleep(60 * 5)
        return None
    profile = webdriver.FirefoxOptions()
    # profile.add_argument('-headless')  # 设置无头模式
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.http', IP)  # IP为你的代理服务器地址:如‘127.0.0.0’，字符串类型
    profile.set_preference('network.proxy.http_port', int(PORT))  # PORT为代理服务器端口号:如，9999，整数类型
    while retry_count > 0:
        try:
            driver = webdriver.Chrome(options=profile)
            time.sleep(15)
            driver.set_page_load_timeout(75)    #设置等待时间,保险起见，设为75秒
            driver.set_script_timeout(75)
            driver.get(url)
            element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'hdcontent')))
            time.sleep(random.uniform(5, 20))   #在当前页面随机停留一段时间
            html = driver.page_source
            bf = BeautifulSoup(html, 'html.parser')
            # data = bf.find('div',id='hdtable').find_all('tr')
            driver.close()
            return bf
        except Exception:
            print('错误发生，重新尝试获取，剩余次数{}'.format(retry_count-1))
            retry_count -= 1
            driver.close()
    delete_proxy(proxy)
    print('代理节点：{}：{}不可用，已删除'.format(IP, PORT))
    return None


def trans(a):
    hd = a.find('div',id='hdtable').find_all('tr')
    yl = a.find('div', id='yltable').find_all('tr')
    sk = a.find('div', id='sktable').find_all('tr')
    data_hd = []
    for hang in hd:
        zhandian = []
        for item in hang.contents:
            if item.name == 'td':
                d_str = item.text
                d_str = d_str.replace('↑', '')
                d_str = d_str.replace('↓', '')
                d_str = d_str.replace('—', '')
                zhandian.append(d_str)
        data_hd.append(zhandian)

    data_yl = []
    for hang in yl:
        zhandian = []
        for item in hang.contents:
            if item.name == 'td':
                d_str = item.text
                d_str = d_str.replace('*', '')
                zhandian.append(d_str)
        data_yl.append(zhandian)

    data_sk = []
    for hang in sk:
        zhandian = []
        for item in hang.contents:
            if item.name == 'td':
                d_str = item.text
                d_str = d_str.replace('↑', '')
                d_str = d_str.replace('↓', '')
                d_str = d_str.replace('—', '')
                zhandian.append(d_str)
        data_sk.append(zhandian)
    skdate = a.find('span', id='skdate').text

    return data_hd, data_yl, data_sk, skdate


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def write_data(data, f_str, data1=None, skdate=None):

    if data1 is None:
        dizhi = []
        shijian = []
    else:
        dizhi = [x[3] for x in data1]  # 记录已有地址和时间
        shijian = [x[4] for x in data1]
    # 使用列表解析读取二维列表的单独列  [x[0] for x in data]

    path2 = os.path.join(path1, '水利部官网数据', f_str)
    folder = os.path.exists(path2)
    if not folder:
        os.makedirs(path2)

    # 新爬取结果与旧数据对比，将更新的结果写入文件
    if f_str == '大江大河':
        for hang in data:
            path3 = os.path.join(path1, '水利部官网数据', f_str, hang[0])
            folder = os.path.exists(path3)
            if not folder:
                os.makedirs(path3)
            if dizhi.count(hang[3]) != 0:   #地址存在
                index = dizhi.index(hang[3])    #标记索引
                if hang[4] != shijian[index]:
                    with open(path3 + '\\{}-{}-{}.txt'.format(hang[1], hang[2], hang[3]),
                              'a+',encoding='utf-8') as f:
                        f.write('{}\t{}\t{}\t{} \n'.format(time.strftime("%Y-", time.localtime()) + hang[4],
                                                           hang[5], hang[6], hang[7]))
            else:
                # 当地址不存在时，创建新文件
                with open(path3 + '\\{}-{}-{}.txt'.format(hang[1], hang[2], hang[3]),
                          'a+', encoding='utf-8') as f:
                    f.write('{}\t{}\t{}\t{} \n'.format('时间', '水位（米）', '流量（m^3/s）', '警戒水位（米）'))
                    f.write('{}\t{}\t{}\t{} \n'.format(time.strftime("%Y-", time.localtime()) + hang[4],
                                                       hang[5], hang[6], hang[7]))

    if f_str == '重点雨水情':
        for hang in data:
            path3 = os.path.join(path1, '水利部官网数据', f_str, hang[0])
            folder = os.path.exists(path3)
            if not folder:
                os.makedirs(path3)
            if dizhi.count(hang[3]) != 0:   #地址存在
                index = dizhi.index(hang[3])    #标记索引
                if hang[4] != shijian[index]:
                    with open(path3 + '\\{}-{}-{}.txt'.format(hang[1], hang[2], hang[3]),
                              'a+',encoding='utf-8') as f:
                        f.write('{}\t{}\t{} \n'.format(hang[4],
                                                           hang[5], hang[6]))
            else:
                # 当地址不存在时，创建新文件
                with open(path3 + '\\{}-{}-{}.txt'.format(hang[1], hang[2], hang[3]),
                          'a+', encoding='utf-8') as f:
                    f.write('{}\t{}\t{} \n'.format('时间', '日雨量(毫米)', '天气'))
                    f.write('{}\t{}\t{} \n'.format(hang[4],
                                                   hang[5], hang[6]))

    if f_str == '大型水库':
        for hang in data:
            path3 = os.path.join(path1, '水利部官网数据', f_str, hang[0])
            folder = os.path.exists(path3)
            if not folder:
                os.makedirs(path3)
            if dizhi.count(hang[3]) != 0:   #地址存在
                with open(path3 + '\\{}-{}-{}.txt'.format(hang[1], hang[2], hang[3]),
                              'a+',encoding='utf-8') as f:
                    f.write('{}\t{}\t{}\t{}\t{} \n'.format(skdate, hang[4],
                                                           hang[5], hang[6], hang[7]))
            else:
                # 当地址不存在时，创建新文件
                with open(path3 + '\\{}-{}-{}.txt'.format(hang[1], hang[2], hang[3]),
                          'a+', encoding='utf-8') as f:
                    f.write('{}\t{}\t{}\t{}\t{} \n'.format('时间', '库水位(米)', '需水量(亿立方米)','入库(米^3/秒)','堤顶高程(米)'))
                    f.write('{}\t{}\t{}\t{}\t{} \n'.format(skdate, hang[4],
                                                           hang[5], hang[6], hang[7]))
    return data


def time_sleep():
    print('{}时间数据爬取完成'.format(time.strftime("%m-%d-%H", time.localtime())))
    now = datetime.datetime.now()
    sleep_time = 36 + random.uniform(1, 10)
    end = now + datetime.timedelta(days=sleep_time / 86400)
    print('开始休眠，将休眠至：{}'.format(end))
    time.sleep(sleep_time)


if __name__ == '__main__':
    path1 = os.path.abspath('.')  # 获取当前脚本所在的路径
    folder = os.path.exists(path1 + '\\水利部官网数据')
    if not folder:
        os.makedirs(path1 + '\\水利部官网数据')
    print('爬虫开始运行')
    url = 'http://xxfb.hydroinfo.gov.cn/ssIndex.html'
    a_ex = None
    while a_ex is None:
        a_ex = get_data(url)

    hd, yl, sk, skdate = trans(a_ex)
    hd_ex = write_data(hd, '大江大河')
    yl_ex = write_data(yl, '重点雨水情')
    sk_ex = write_data(sk, '大型水库', skdate=skdate)
    skdate_ex = skdate
    time_sleep()

    # 主循环，保留
    while True:
        a = None
        while a is None:
            a = get_data(url)
        hd, yl, sk, skdate = trans(a)
        hd_ex = write_data(hd, '大江大河', hd_ex)
        yl_ex = write_data(yl, '重点雨水情', yl_ex)
        if skdate == skdate_ex:
            pass
        else:
            sk_ex = write_data(sk, '大型水库', sk_ex, skdate=skdate)
            skdate_ex = skdate
        time_sleep()




