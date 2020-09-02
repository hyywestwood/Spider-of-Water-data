# -*- coding: utf-8 -*-
# @Time    : 2020/9/2 19:22
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : water_data_spider.py
# @Software: PyCharm
import datetime
import os
import requests
import time
import json
import re
from ashx import Spider_ajax


class Water_data_spider():
    def __init__(self):
        self.url = {
            '大江大河': 'http://xxfb.mwr.cn/hydroSearch/greatRiver',
            '大型水库': 'http://xxfb.mwr.cn/hydroSearch/greatRsvr',
            '重点雨水情': 'http://xxfb.mwr.cn/hydroSearch/pointHydroInfo',
        }
        self.path = os.path.abspath(os.path.join('.', '水利部-新版数据'))  # 数据文件存储路径
        self.retry_counts = 5
        self.data = None
        self.headers = {
            'Host': 'xxfb.mwr.cn',
            'Referer': 'http://xxfb.mwr.cn/sq_dxsk.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
        }

    def run(self):
        self.data = self.get_data(self.url['大江大河'])
        self.write_file_djdh(self.data, 'test')

    def get_data(self, target_url):
        self.retry_counts = 5
        while self.retry_counts > 0:
            r = requests.get(target_url, headers=self.headers)
            if r.status_code == 200:
                data_get = json.loads(r.text)
                results = data_get["result"]["data"]
                return results
            else:
                print('访问拒绝：' + str(r.status_code))
                time.sleep(10)
                self.retry_counts -= 1
        return None

    def write_file_djdh(self, results, f_str):
        assert results is not None
        path2 = os.path.join(self.path, f_str)
        folder = os.path.exists(path2)
        if not folder:
            os.makedirs(path2)

        for hang in results:
            path3 = os.path.join(self.path, f_str, hang['poiBsnm'])
            folder = os.path.exists(path3)
            if not folder:
                os.makedirs(path3)
            with open(path3 + '\\{}-{}-{}.txt'.format(hang['poiAddv'].strip(), hang['rvnm'].strip(), hang['stnm'].strip()),
                      'a+', encoding='utf-8') as f:
                f.write('{}\t\t{}\t{}\t{} \n'.format(hang['tm'], hang['zl'], hang['ql'], hang['wrz']))


if __name__ == '__main__':
    spider = Water_data_spider()
    spider.run()
    # url = 'http://xxfb.mwr.cn/hydroSearch/greatRiver'
    # headers = {
    #     'Host': 'xxfb.mwr.cn',
    #     'Referer': 'http://xxfb.mwr.cn/sq_dxsk.html',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
    # }
    # r = requests.get(url, headers=headers)
    # data_get = json.loads(r.text)
    # results = data_get["result"]["data"]
    # hang = results[0]
    #
    # with open('.\\{}-{}-{}.txt'.format(hang['poiAddv'].strip(), hang['rvnm'].strip(), hang['stnm'].strip()),
    #           'a+', encoding='utf-8') as f:
    #     f.write('{}\t\t{}\t{}\t{} \n'.format(hang['tm'], hang['zl'], hang['ql'], hang['wrz']))