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
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import configparser


class Water_data_spider():
    def __init__(self):
        self.url = {
            '大江大河': 'http://xxfb.mwr.cn/hydroSearch/greatRiver',
            '大型水库': 'http://xxfb.mwr.cn/hydroSearch/greatRsvr',
            '重点雨水情': 'http://xxfb.mwr.cn/hydroSearch/pointHydroInfo',
        }
        self.path = os.path.abspath(os.path.join('.', '水利部新版数据'))  # 数据文件存储路径
        self.retry_counts = 5
        self.flag = 1  # 用于控制发邮件进行通知的时间
        self.djdh = None
        self.dxsk = None
        self.zdysq = None
        self.headers = {
            'Host': 'xxfb.mwr.cn',
            'Referer': 'http://xxfb.mwr.cn/sq_dxsk.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
        }

    def run(self):
        while True:
            self.djdh = self.get_data(self.url['大江大河'])
            self.write_file(self.djdh, '大江大河')
            self.dxsk = self.get_data(self.url['大型水库'])
            self.write_file(self.dxsk, '大型水库')
            self.zdysq = self.get_data(self.url['重点雨水情'])
            self.write_file(self.zdysq, '重点雨水情')
            self.report_time = self.dxsk[0]['tm'][:10]
            self.get_qgryl('全国日雨量')

            self.time_sleep(8*3600)
            # 爬取六次数据之后，发邮件通知
            if self.flag % 6 == 1:
                run_stage = '时间：' + time.strftime("%Y-%m-%d-%H", time.localtime()) + '抓取完成'
                self.email_send(run_stage, '水利数据' + time.strftime("%Y-%m-%d-%H", time.localtime()))
            self.flag = self.flag + 1

    def get_data(self, target_url):
        self.retry_counts = 5
        while self.retry_counts > 0:
            r = requests.get(target_url, headers=self.headers)
            if r.status_code == 200:
                # 数据处理
                data_get = json.loads(r.text)
                results = data_get["result"]["data"]
                time.sleep(60)
                return results
            else:
                print('访问拒绝：' + str(r.status_code))
                time.sleep(10)
                self.retry_counts -= 1
        return None

    def get_qgryl(self, f_str):
        path2 = os.path.join(self.path, f_str)
        folder = os.path.exists(path2)
        if not folder:
            os.makedirs(path2)

        url = 'http://xxfb.mwr.cn/hydroSearch/nationalDailyRainfall'
        r = requests.get(url, headers=self.headers, stream=True)
        time.sleep(10)
        if r.status_code == 200:
            open(os.path.join(path2, self.report_time + '.png'), 'wb').write(r.content)  # 将内容写入图片
            print(self.report_time+'.png 已成功保存')
            time.sleep(10)

    def write_file(self, results, f_str):
        assert results is not None
        path2 = os.path.join(self.path, f_str)
        folder = os.path.exists(path2)
        if not folder:
            os.makedirs(path2)

        if f_str == '大江大河':
            for hang in results:
                path3 = os.path.join(self.path, f_str, hang['poiBsnm'].strip())
                folder = os.path.exists(path3)
                if not folder:
                    os.makedirs(path3)
                with open(path3 + '\\{}-{}-{}.txt'.format(hang['poiAddv'].strip(), hang['rvnm'].strip(), hang['stnm'].strip()),
                          'a+', encoding='utf-8') as f:
                    f.write('{}\t\t{}\t{}\t{} \n'.format(hang['tm'], hang['zl'], hang['ql'], hang['wrz']))

        if f_str == '大型水库':
            for hang in results:
                path3 = os.path.join(self.path, f_str, hang['poiBsnm'].strip())
                folder = os.path.exists(path3)
                if not folder:
                    os.makedirs(path3)
                with open(path3 + '\\{}-{}-{}.txt'.format(hang['poiAddv'].strip(), hang['rvnm'].strip(), hang['stnm'].strip()),
                                  'a+',encoding='utf-8') as f:
                    f.write('{}\t\t{}\t{}\t{}\t{} \n'.format(hang['tm'], hang['rz'], hang['wl'], hang['inq'], hang['damel']))

        if f_str == '重点雨水情':
            for hang in results:
                path3 = os.path.join(self.path, f_str, hang['poiBsnm'].strip())
                folder = os.path.exists(path3)
                if not folder:
                    os.makedirs(path3)
                # temp = hang['stnm'].strip()
                # temp = temp.replace('*', '')
                # temp = temp.replace('/', '-')
                with open(path3 + '\\{}-{}-{}.txt'.format(hang['poiAddv'].strip(), hang['rvnm'].strip().replace('/', '-'),
                                                          hang['stnm'].strip().replace('*', '')),'a+',encoding='utf-8') as f:
                    f.write('{}\t\t{}\t{}\t{}\t{} \n'.format(hang['tm'], hang['dyp'], hang['wth'], hang['lat'], hang['lgt']))

    def time_sleep(self, sleep_time=8*3600):
        print('{}数据爬取完成'.format(time.strftime("%m-%d-%H", time.localtime())))
        now = datetime.datetime.now()
        end = now + datetime.timedelta(days=sleep_time / 86400)
        print('开始休眠，将休眠至：{}'.format(end))
        time.sleep(sleep_time)

    def email_send(self, text, subject):
        # 读取email配置
        config = configparser.ConfigParser()
        config.read("./config.cfg")
        conf_email = config['email_setting']

        sender = conf_email['sender']
        receivers = conf_email['receivers'].split(',')  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        mail_host = conf_email['mail_host']  # 设置服务器
        mail_user = conf_email['mail_user']  # 用户名
        mail_pass = conf_email['mail_pass']  # 口令

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
    spider = Water_data_spider()
    spider.run()
    # url = 'http://xxfb.mwr.cn/hydroSearch/greatRiver'
    # headers = {
    #     'Host': 'xxfb.mwr.cn',
    #     'Referer': 'http://xxfb.mwr.cn/sq_dxsk.html',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
    # }
    # r = requests.get(url, headers=headers)
    # cookies = r.cookies.items()
    # cookie = ''
    # for name, value in cookies:
    #     cookie += '{0}={1};'.format(name, value)
    # data_get = json.loads(r.text)
    # results = data_get["result"]["data"]
    # hang = results[0]
    #
    # with open('.\\{}-{}-{}.txt'.format(hang['poiAddv'].strip(), hang['rvnm'].strip(), hang['stnm'].strip()),
    #           'a+', encoding='utf-8') as f:
    #     f.write('{}\t\t{}\t{}\t{} \n'.format(hang['tm'], hang['zl'], hang['ql'], hang['wrz']))