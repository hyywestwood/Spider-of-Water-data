# -*- coding: utf-8 -*-
# @Time    : 2020/9/2 15:43
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : ashx.py
# @Software: PyCharm
"""
本程序尝试分析水质数据实时发布系统的网络请求，
采用直接构造请求的方式获取水质数据
从而省去了selenium的使用
"""
import datetime
import os
import requests
import time
import json
import re


class Spider_ajax():
    def __init__(self, url):
        self.url = url
        self.path = os.path.abspath(os.path.join('.', '水质数据'))  # 数据文件存储路径
        self.data = None
        self.headers = {
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'Keep-Alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': '106.37.208.243:8068',
            'Origin': 'http://106.37.208.243:8068',
            'Referer': 'http://106.37.208.243:8068/GJZ/Business/Publish/RealData.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
        }
        self.post_data = {
            'AreaID': '',
            'RiverID': '',
            'MNName': '',
            'PageIndex': '1',
            'PageSize': '60',
            'action': 'getNewData'
        }

    def run(self):
        while True:
            self.data = self.get_data()
            self.write_file(self.data, '新版Plus')
            self.time_sleep(4*3600)

    def time_sleep(self, sleep_time=8 * 3600):
        print('{}数据爬取完成'.format(time.strftime("%m-%d-%H", time.localtime())))
        now = datetime.datetime.now()
        end = now + datetime.timedelta(days=sleep_time / 86400)
        print('开始休眠，将休眠至：{}'.format(end))
        time.sleep(sleep_time)

    def get_data(self):
        r = requests.post(self.url, data=self.post_data, headers=self.headers)
        data_get = json.loads(r.text)
        pattern = re.compile(r'<[^>]+>', re.S)
        variables_name = list(map(lambda x: pattern.sub('', x), data_get["thead"]))

        result = []
        for item in data_get["tbody"]:
            item = list(map(lambda x: ('' if x is None else x), item))
            result.append(list(map(lambda x: pattern.sub('', x), item)))

        return result

    def write_file(self, result, f_str):
        assert result is not None
        path2 = os.path.join(self.path, f_str)
        folder = os.path.exists(path2)
        if not folder:
            os.makedirs(path2)

        for hang in result:
            path3 = os.path.join(path2, hang[0])
            folder = os.path.exists(path3)
            if not folder:
                os.makedirs(path3)
            with open(path3 + '\\{}-{}.txt'.format(hang[1], hang[2]), 'a+', encoding='utf-8') as f:
                f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t \n'.format(
                    time.strftime("%Y-", time.localtime()) + hang[3],
                    hang[4], hang[5], hang[6], hang[7], hang[8], hang[9], hang[10], hang[11], hang[12], hang[13],
                    hang[14], hang[15], hang[16]))


if __name__ == '__main__':
    url = 'http://106.37.208.243:8068/GJZ/Ajax/Publish.ashx'
    spider = Spider_ajax(url)
    spider.run()

