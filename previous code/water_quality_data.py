# -*- coding: utf-8 -*-
# @Time    : 2019/4/23 14:01
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : water_quality_data.py
# @Software: PyCharm
import requests
import time
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def get_data(url, value, num_retries = 2):
    try:
        req = requests.post(url, data=value, headers=headers)
        data = req.json()
    except Exception as e:
        print('下载出了点问题：', req.status_code)
        if num_retries > 0:
            if 500 <= req.status_code < 600:
                time.sleep(10)
                return get_data(url, num_retries-1)
    return data


def email_send(text, time):
    sender = ' 3140105713@zju.edu.cn'
    receivers = ['1554148540@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    mail_host = "smtp.zju.edu.cn"  # 设置服务器
    mail_user = "3140105713@zju.edu.cn"  # 用户名
    mail_pass = "5896westwood"  # 口令

    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = Header("水质数据", 'utf-8')  # 发送者
    message['To'] = Header("hyy", 'utf-8')  # 接收者

    subject = '水质数据获取情况' + time
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
    path1 = os.path.abspath('.')  # 获取当前脚本所在的路径
    folder = os.path.exists(path1 + '\\水质数据')
    if not folder:
        os.makedirs(path1 + '\\水质数据')
    print('爬虫开始运行')
    headers = {
        'Host': '123.127.175.45:8082',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'http://123.127.175.45:8082/',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Length': '21',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }
    value = {
        'Method': 'SelectRealData'
    }
    url = 'http://123.127.175.45:8082/ajax/GwtWaterHandler.ashx'
    # url = 'http://www.baidu.com'
    data_ex = requests.post(url, data=value, headers=headers).json()
    for item in data_ex:
        with open(path1+ '\\水质数据\\' + item['siteName'] + '.txt', 'w', encoding='utf-8') as f:
            f.write('时间     PH     溶解氧DO        氨氮NH4       高锰酸盐指数      总有机碳        水质类别        '
                    '断面属性        站点情况 \n')
            f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{} \n'.format(item['dateTime'], item['pH'],
                                                                item['DO'], item['NH4'], item['CODMn'],
                                                                item['TOC'], item['level'], item['attribute'], item['status']))

    print('初始数据爬取完成')
    flag = 1
    while True:
        print('sleep now')
        time.sleep(random.uniform(1,8*60*60))
        data = get_data(url, value)
        for i in range(len(data)):
            if data[i]['dateTime'] == data_ex[i]['dateTime']:
                continue
            else:
                item = data[i]
                with open(path1 + '\\水质数据\\' + item['siteName'] + '.txt', 'a', encoding='utf-8') as f:
                    f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{} \n'.format(item['dateTime'], item['pH'],
                                                                           item['DO'], item['NH4'], item['CODMn'],
                                                                           item['TOC'], item['level'],
                                                                           item['attribute'], item['status']))
        data_ex = data
        if flag % 10 == 1:
            run_stage = '爬取时间:{}'.format(data[0]['dateTime'])
            email_send(run_stage, data[0]['dateTime'])
        print('此时间爬取完成：', end='')
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        flag += 1
