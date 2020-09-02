# -*- coding: utf-8 -*-
# @Time    : 2020/8/30 20:23
# @Author  : hyy
# @Email   : hyywestwood@zju.edu.cn
# @File    : spider_1.py
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
from selenium.webdriver.common.action_chains import ActionChains
import smtplib
from email.mime.text import MIMEText
from email.header import Header


class Spider():
    def __init__(self, url):
        self.url = url
        self.flag = 1  # 用于控制发邮件进行通知的时间
        self.retry_counts = 3
        self.report_time = None
        self.djdh = None
        self.dxsk = None
        self.zdysq = None
        self.qgryl = None
        self.path = os.path.abspath(os.path.join('.', '水利部-新版数据'))  # 数据文件存储路径
        self.folder = os.path.exists(self.path)  # 判断存储路径文件夹是否存在，没有则创建
        if not self.folder:
            os.makedirs(self.path)

    def run(self):
        # 死循环，让爬虫一直运行
        while True:
            self.driver = self.getdriver(self.url)
            self.djdh = None
            # 获取水利部官网数据
            while self.djdh is None:
                self.djdh = self.get_data()
                click_btn = self.driver.find_element_by_xpath('//a[li="大型水库"]')
                ActionChains(self.driver).click(click_btn).perform()
                self.dxsk = self.get_data()
                click_btn = self.driver.find_element_by_xpath('//a[li="重点雨水情"]')
                ActionChains(self.driver).click(click_btn).perform()
                self.zdysq = self.get_data()
                click_btn = self.driver.find_element_by_xpath('//a[li="全国日雨量"]')
                ActionChains(self.driver).click(click_btn).perform()
                self.get_qgryl('全国日雨量')

            self.driver.close()  # 浏览器关闭
            self.write_data(self.djdh, '大江大河')  # 将获取的数据写入文件，简单起见，不设置新旧数据对比
            self.write_data(self.dxsk, '大型水库')
            self.write_data(self.zdysq, '重点雨水情')
            self.time_sleep()  # 爬虫休眠

            # 爬取六次数据之后，发邮件通知
            if self.flag % 6 == 1:
                run_stage = '时间：' + time.strftime("%Y-%m-%d-%H", time.localtime()) + '抓取完成'
                self.email_send(run_stage, '水利数据'+time.strftime("%Y-%m-%d-%H", time.localtime()))
            self.flag = self.flag + 1

    def getdriver(self, url, Headless=True):
        profile = webdriver.FirefoxOptions()
        user_agent = 'Mozilla/5.0 (Linux; Android 7.0; BND-AL10 Build/HONORBND-AL10; wv) ' \
                     'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 ' \
                     'MQQBrowser/6.2 TBS/044304 Mobile Safari/537.36 MicroMessenger/6.7.3.1340(0x26070331) ' \
                     'NetType/4G Language/zh_CN Process/tools'
        if Headless:
            profile.add_argument('-headless')  # 设置无头模式
        # profile.set_preference('network.proxy.type', 1)
        profile.set_preference('general.useragent.override', user_agent)
        driver = webdriver.Firefox(options=profile)
        driver.get(url)
        return driver

    def get_qgryl(self, f_str):
        path2 = os.path.join(self.path, f_str)
        folder = os.path.exists(path2)
        if not folder:
            os.makedirs(path2)

        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept - Encoding': 'gzip, deflate',
                   'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                   'Connection': 'Keep-Alive',
                   'Host': 'xxfb.mwr.cn',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
                   'Referer': 'http://xxfb.mwr.cn/sq_qgryl.html',
                   'Upgrade-Insecure-Requests': '1'}
        time.sleep(5)
        bf = BeautifulSoup(self.driver.page_source, 'html.parser')
        img = bf.find('div', id='hdcontent').find_all('img')
        url = 'http://xxfb.mwr.cn' + img[0].attrs['src']
        # print(url)
        r = requests.get(url, headers=headers, stream=True)
        if r.status_code == 200:
            open(os.path.join(path2, self.report_time + '.png'), 'wb').write(r.content)  # 将内容写入图片
            print(self.report_time+'.png 已成功保存')
            time.sleep(10)
            # open(r'D:\pycharm\pachong\水利部-新版数据\全国日雨量\test2.png', 'wb').write(r.content)  # 将内容写入图片

    def get_data(self):
        while self.retry_counts > 0:
            try:
                time.sleep(random.uniform(80, 100))  # 需要停留足够长的时间确保数据加载出来
                WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, 'hdcontent')))
                retrytimes = 10
                while retrytimes > 0:
                    time.sleep(30*1)
                    html = self.driver.page_source
                    bf = BeautifulSoup(html, 'html.parser')
                    self.report_time = str(bf.find('span', id='hddate').contents[0])
                    data_hd = self.trans(bf)
                    retrytimes -= 1
                    if data_hd:
                        return data_hd
                return None
            except Exception:
                print('错误发生，重新尝试获取，剩余次数{}'.format(self.retry_counts-1))
                self.retry_counts -= 1
        return None

    def trans(self, a):
        hd = a.find('div',id='hdtable').find_all('tr')
        data_hd = []
        for hang in hd:
            zhandian = []
            for item in hang.contents:
                if item.name == 'td':
                    d_str = item.text
                    d_str = d_str.replace('↑', '')
                    d_str = d_str.replace('↓', '')
                    d_str = d_str.replace('—', '')
                    d_str = d_str.replace('*', '')
                    d_str = d_str.replace('?', '')
                    d_str = d_str.replace('/', '')
                    d_str = d_str.replace('|', '')
                    d_str = d_str.replace(':', '')
                    zhandian.append(d_str.strip())
            data_hd.append(zhandian)
        return data_hd

    def write_data(self, data, f_str):
        path2 = os.path.join(self.path, f_str)
        folder = os.path.exists(path2)
        if not folder:
            os.makedirs(path2)

        if f_str == '大江大河':
            for hang in data:
                path3 = os.path.join(self.path, f_str, hang[0])
                folder = os.path.exists(path3)
                if not folder:
                    os.makedirs(path3)
                with open(path3 + '\\{}-{}-{}.txt'.format(hang[1], hang[2], hang[3]),
                                  'a+',encoding='utf-8') as f:
                    f.write('{}\t{}\t{}\t{} \n'.format(time.strftime("%Y-", time.localtime()) + hang[4],
                                                               hang[5], hang[6], hang[7]))

        if f_str == '大型水库':
            for hang in data:
                path3 = os.path.join(self.path, f_str, hang[0])
                folder = os.path.exists(path3)
                if not folder:
                    os.makedirs(path3)
                with open(path3 + '\\{}-{}-{}.txt'.format(hang[1], hang[2], hang[3]),
                                  'a+',encoding='utf-8') as f:
                    f.write('{}\t{}\t{}\t{} \n'.format(self.report_time, hang[4],
                                                               hang[5], hang[6], hang[7]))

        if f_str == '重点雨水情':
            for hang in data:
                path3 = os.path.join(self.path, f_str, hang[0])
                folder = os.path.exists(path3)
                if not folder:
                    os.makedirs(path3)
                with open(path3 + '\\{}-{}-{}.txt'.format(hang[1], hang[2], hang[3]),
                                  'a+',encoding='utf-8') as f:
                    f.write('{}\t{}\t{} \n'.format(hang[4],hang[5], hang[6]))

    def time_sleep(self, sleep_time=8*3600):
        print('{}数据爬取完成'.format(time.strftime("%m-%d-%H", time.localtime())))
        now = datetime.datetime.now()
        end = now + datetime.timedelta(days=sleep_time / 86400)
        print('开始休眠，将休眠至：{}'.format(end))
        time.sleep(sleep_time)

    def email_send(self, text, subject):
        sender = ' 3140105713@zju.edu.cn'
        receivers = ['1554148540@qq.com', '825548473@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        mail_host = "smtp.zju.edu.cn"  # 设置服务器
        mail_user = "3140105713@zju.edu.cn"  # 用户名
        mail_pass = "5896westwood"  # 口令

        # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
        message = MIMEText(text, 'plain', 'utf-8')
        message['From'] = Header("水利数据", 'utf-8')  # 发送者
        message['To'] = Header("hyy", 'utf-8')  # 接收者

        message['Subject'] = Header(subject, 'utf-8')

        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")


if __name__ == '__main__':
    url = 'http://xxfb.mwr.cn/sq_djdh.html'
    Web_spider = Spider(url)
    Web_spider.run()





