# -*- coding: utf-8 -*-
# @Time    : 2020/8/31 10:34
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : Water_Quality_spider.py
# @Software: PyCharm
import os
import time
import random

import schedule
from bs4 import BeautifulSoup
from water_data_spider import Spider


class Quality_spider(Spider):
    def __init__(self, url):
        self.url = url
        self.retry_counts = 3
        self.water_quality = None
        self.path = os.path.abspath(os.path.join('.', '水质数据'))  # 数据文件存储路径
        self.folder = os.path.exists(self.path)  # 判断存储路径文件夹是否存在，没有则创建
        if not self.folder:
            os.makedirs(self.path)
        self.driver = self.getdriver(self.url)
        self.logger = self.log_setting()

    def run(self):
        # schedule.every(10).minutes.do(self.single_process)
        schedule.every().day.at("09:00").do(self.single_process)
        schedule.every().day.at("13:00").do(self.single_process)
        schedule.every().day.at("17:00").do(self.single_process)
        schedule.every().day.at("21:00").do(self.single_process)
        text = '水质数据爬取完成'
        subject = '水质数据'
        schedule.every(3).days.at("22:30").do(self.email_send, text, subject)
        while True:
            schedule.run_pending()

    def single_process(self):
        time.sleep(30)
        # 获取水质数据
        self.water_quality = None
        while self.water_quality is None and self.retry_counts > 0:
            self.water_quality = self.get_data()

        if self.water_quality is None:
            self.logger.warning("水质数据抓取失败")
        else:
            self.write_data(self.water_quality, '新版')  # 将获取的数据写入文件，简单起见，不设置新旧数据对比
            self.logger.info("水质数据抓取完成")

    def get_data(self):
        try:
            # time.sleep(60)  # 需要停留足够长的时间确保数据加载出来
            # WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'panel')))
            self.driver.refresh()
            time.sleep(60*2)
            iframe = self.driver.find_element_by_tag_name("iframe")
            self.driver.switch_to.frame(iframe)   # 网页中存在iframe需要switch一下才能正确得到结果
            html = self.driver.page_source
            bf = BeautifulSoup(html, 'html.parser')
            data_hd = self.trans(bf.find_all('tr'))
            if data_hd:
                return data_hd
            self.retry_counts -= 1
            return None
        except Exception:
            print('错误发生，重新尝试获取，剩余次数{}'.format(self.retry_counts-1))
            self.retry_counts -= 1
            return None

    def trans(self, a):
        data = []
        for i in range(1, len(a)):
            shuju = []
            d_str = a[i].contents
            for item in d_str:
                if item.name == 'td':
                    shuju.append(item.text)
            data.append(shuju)
        return data

    def write_data(self, data, f_str):
        assert data is not None
        path2 = os.path.join(self.path, f_str)
        folder = os.path.exists(path2)
        if not folder:
            os.makedirs(path2)

        for hang in data:
            path3 = os.path.join(self.path, f_str, hang[0])
            folder = os.path.exists(path3)
            if not folder:
                os.makedirs(path3)
            with open(os.path.join(path3, '{}-{}.txt'.format(hang[1], hang[2])), 'a+', encoding='utf-8') as f:
                f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t \n'.format(time.strftime("%Y-", time.localtime()) + hang[3],
                                                    hang[4], hang[5],hang[6],hang[7],hang[8],hang[9],hang[10],hang[11],hang[12],hang[13],
                                                                                             hang[14],hang[15],hang[16]))


if __name__ == '__main__':
    url = 'http://106.37.208.243:8068/GJZ/Business/Publish/Main.html'
    spider = Quality_spider(url)
    spider.run()