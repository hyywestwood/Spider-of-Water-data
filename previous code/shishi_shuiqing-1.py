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
    message['From'] = Header("江河数据", 'utf-8')  # 发送者
    message['To'] = Header("hyy", 'utf-8')  # 接收者

    subject = '大江大河水情获取情况' + time
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
    # profile.add_argument('-headless')  # 设置无头模式
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.http', IP)  # IP为你的代理服务器地址:如‘127.0.0.0’，字符串类型
    profile.set_preference('network.proxy.http_port', int(PORT))  # PORT为代理服务器端口号:如，9999，整数类型
    while retry_count > 0:
        try:
            driver = webdriver.Firefox(options=profile)
            time.sleep(15)
            driver.set_page_load_timeout(75)    #设置等待时间,保险起见，设为75秒
            driver.set_script_timeout(75)
            driver.get(url)
            element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'row')))
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
        d_str = a[i].text
        d_str = d_str.replace('↑', '')
        d_str = d_str.replace('↓', '')
        d_str = d_str.replace('—', '')
        d_str = d_str.replace('\xa0', '')
        d_str = d_str.rstrip()[1:len(d_str)]
        data.append(d_str.split('\n'))
    return data


def write_data(a, flag, a_ex):

    # 对数据a,a_ex进行处理
    data = trans(a)
    data1 = trans(a_ex)

    dizhi = [x[3] for x in data1]   #记录已有地址和时间
    shijian = [x[4] for x in data1]
    # 使用列表解析读取二维列表的单独列  [x[0] for x in data]

    # 新爬取结果与旧数据对比，将更新的结果写入文件
    for hang in data:
        print(hang)
        if dizhi.count(hang[3]) != 0:   #地址存在
            index = dizhi.index(hang[3])    #标记索引
            if hang[4] != shijian[index]:
                with open(path1 + '\\大江大河实时水情\\' + hang[0] + '\\' + '{}-{}-{}.txt'.format(hang[1], hang[2], hang[3]),
                          'a',encoding='utf-8') as f:
                    f.write('{}\t{}\t{}\t{} \n'.format(time.strftime("%Y-", time.localtime()) + hang[4],
                                                       hang[5], hang[6],hang[7]))
        else:
            # 当地址不存在时，创建新文件
            with open(path1 + '\\大江大河实时水情\\' + hang[0] + '\\' + '{}-{}-{}.txt'.format(hang[1], hang[2], hang[3]),
                      'w', encoding='utf-8') as f:
                f.write('{}\t{}\t{}\t{} \n'.format('时间', '水位（米）', '流量（m^3/s）', '警戒水位（米）'))
    a_ex = a
    flag += 1
    if flag % 6 == 1:
        run_stage = '爬取时间:{}'.format(time.strftime("%Y-", time.localtime()) + data[1][4])
        email_send(run_stage, data[1][4])
        # pass
    now = datetime.datetime.now()
    sleep_time = 3600*6 + random.uniform(1, 3600*4)
    # sleep_time = random.uniform(1, 8)
    end = now + datetime.timedelta(days=sleep_time / 86400)
    print('开始休眠，将休眠至：{}'.format(end))
    time.sleep(sleep_time)
    return flag, a_ex


if __name__ == '__main__':
    path1 = os.path.abspath('.')  # 获取当前脚本所在的路径
    folder = os.path.exists(path1 + '\\大江大河实时水情')
    if not folder:
        os.makedirs(path1 + '\\大江大河实时水情')
    print('爬虫开始运行')
    url = 'http://ditu.92cha.com/shuiqing.php?w=hd'
    a_ex = None
    while a_ex == None:
        a_ex = get_data(url)
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
    flag = 0
    while True:
        a = None
        while a == None:
            a = get_data(url)
        flag, a_ex = write_data(a, flag, a_ex)


