# -*- coding: utf-8 -*-
# @Time    : 2019/6/15 12:06
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : water_quality_data_2.py
# @Software: PyCharm
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


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


def get_data(url):
    retry_count = 3
    proxy = get_proxy()
    # 设置代理服务器
    try:
        IP, PORT = proxy.decode('utf-8').split(':')
    except Exception:
        print('可用代理为空，等待5分钟')
        time.sleep(60*5)
        return None
    profile = webdriver.FirefoxOptions()
    user_agent = 'Mozilla/5.0 (Linux; Android 7.0; BND-AL10 Build/HONORBND-AL10; wv) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 ' \
                 'MQQBrowser/6.2 TBS/044304 Mobile Safari/537.36 MicroMessenger/6.7.3.1340(0x26070331) ' \
                 'NetType/4G Language/zh_CN Process/tools'
    profile.add_argument('-headless')  # 设置无头模式
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.http', IP)  # IP为你的代理服务器地址:如‘127.0.0.0’，字符串类型
    profile.set_preference('network.proxy.http_port', int(PORT))  # PORT为代理服务器端口号:如，9999，整数类型
    profile.set_preference('general.useragent.override', user_agent)
    while retry_count > 0:
        try:
            driver = webdriver.Firefox(options=profile)
            time.sleep(15)
            driver.set_page_load_timeout(75)    #设置等待时间,保险起见，设为75秒
            driver.set_script_timeout(75)
            driver.get(url)
            element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'panel')))
            time.sleep(random.uniform(1, 20))   #在当前页面随机停留一段时间
            html = driver.page_source
            bf = BeautifulSoup(html, 'html.parser')
            data = bf.find_all('tr')
            driver.close()
            return data
        except Exception:
            print('错误发生，重新尝试获取，剩余次数{}'.format(retry_count-1))
            retry_count -= 1
            driver.close()
    delete_proxy(proxy)
    print('代理节点：{}：{}不可用，已删除'.format(IP,PORT))
    return None


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def trans(a):
    data = []
    for i in range(1,len(a)):
        shuju = []
        d_str = a[i].contents
        for item in d_str:
            if item.name == 'td':
                shuju.append(item.text)
        data.append(shuju)
    return data


def write_data(a, flag):
    # 对数据a进行处理,方便起见不做数据清洗
    data = trans(a)
    # dizhi = [x[0] for x in data1]   #记录已有地址和时间
    # shijian = [x[1] for x in data1]
    # 使用列表解析读取二维列表的单独列  [x[0] for x in data]

    for hang in data:
        f_path = path1 + '\\水质数据1\\' + '{}.txt'.format(hang[0])
        if os.path.exists(f_path):
            with open(f_path, 'a+', encoding='utf-8') as f:
                f.write('{}\t\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{} \n'.format(hang[1], hang[2], hang[3], hang[4],
                                                                         hang[5], hang[6], hang[7], hang[8], hang[9]))
        else:
            with open(f_path, 'a+', encoding='utf-8') as f:
                f.write('{}\t\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{} \n'.format('时间', 'pH', '溶解氧', '氨氮',
                                                                         '高锰酸盐', '总有机碳', '水质类别',
                                                                         '断面属性', '站点情况'))
                f.write('{}\t\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{} \n'.format(hang[1], hang[2], hang[3], hang[4],
                                                                         hang[5], hang[6], hang[7], hang[8], hang[9]))
    flag += 1
    if flag % 12 == 1:
        run_stage = '爬取时间:{}'.format(data[1][1])
        email_send(run_stage, data[1][1])
        # pass
    now = datetime.datetime.now()
    sleep_time = 3600*6 + random.uniform(1, 600)
    # sleep_time = random.uniform(1, 8)
    end = now + datetime.timedelta(days=sleep_time / 86400)
    print('开始休眠，将休眠至：{}'.format(end))
    time.sleep(sleep_time)
    return flag


def write_data_1(a):
    data = trans(a)
    for hang in data:
        with open(path1 + '\\水质数据1\\' + '{}.txt'.format(hang[0]),
                  'w', encoding='utf-8') as f:
            f.write('{}\t\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{} \n'.format('时间', 'pH', '溶解氧', '氨氮',
                                                                     '高锰酸盐', '总有机碳', '水质类别',
                                                                     '断面属性', '站点情况'))
            f.write('{}\t\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{} \n'.format(hang[1], hang[2], hang[3], hang[4],
                                                                     hang[5], hang[6], hang[7], hang[8], hang[9]))


if __name__ == '__main__':
    path1 = os.path.abspath('.')  # 获取当前脚本所在的路径
    folder = os.path.exists(path1 + '\\水质数据1')
    if not folder:
        os.makedirs(path1 + '\\水质数据1')
    print('爬虫开始运行')
    url = 'http://123.127.175.45:8082'

    flag = 0
    while True:
        a = None
        while a is None:
            a = get_data(url)
        flag = write_data(a, flag)

    # 为使代码尽量简单，爬虫舍去了数据清洗的操作（因为需保证网站上数据更新后尽快采集，且单个站点可能因为仪器等原因一直没更新）
    # 即在数据文件中，可能存在较多相同的数据，需要后期再处理一下


