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
from selenium.webdriver.common.action_chains import ActionChains
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def email_send(text, timea):
    sender = ' 3140105713@zju.edu.cn'
    receivers = ['1554148540@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    mail_host = "smtp.zju.edu.cn"  # 设置服务器
    mail_user = "3140105713@zju.edu.cn"  # 用户名
    mail_pass = "5896westwood"  # 口令

    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = Header("水利数据", 'utf-8')  # 发送者
    message['To'] = Header("hyy", 'utf-8')  # 接收者

    subject = '水利数据获取情况' + timea
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
    # proxy = get_proxy()
    # 设置代理服务器
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('User-Agent=Mozilla/5.0 (Linux; U; '
    #                             'Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) '
    #                             'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 '
    #                             'MQQBrowser/8.9 Mobile Safari/537.36')
    # try:
    #     # IP, PORT = proxy.decode('utf-8').split(':')
    #     if random.random() < 0.6:
    #         chrome_options.add_argument('--proxy-server=http://' + proxy.decode('utf-8'))
    #     else:
    #         print('尝试使用本地IP')
    # except Exception:
    #     print('可用代理为空，尝试使用本地IP')
    #     pass
        # time.sleep(60 * 5)
        # return None

    profile = webdriver.FirefoxOptions()
    user_agent = 'Mozilla/5.0 (Linux; Android 7.0; BND-AL10 Build/HONORBND-AL10; wv) ' \
                 'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 ' \
                 'MQQBrowser/6.2 TBS/044304 Mobile Safari/537.36 MicroMessenger/6.7.3.1340(0x26070331) ' \
                 'NetType/4G Language/zh_CN Process/tools'
    profile.add_argument('-headless')  # 设置无头模式
    # profile.set_preference('network.proxy.type', 1)
    profile.set_preference('general.useragent.override', user_agent)

    while retry_count > 0:
        try:
            # driver = webdriver.Chrome(options=chrome_options)
            driver = webdriver.Firefox(options=profile)
            # driver = webdriver.Chrome()
            # driver.set_page_load_timeout(60*5)    #设置等待时间,保险起见，设为75秒
            # driver.set_script_timeout(60*5)
            driver.get(url)
            time.sleep(random.uniform(80, 100))  # 需要停留足够长的时间确保数据加载出来
            # click_btn = driver.find_element_by_xpath('//img[@id="jhimg"]')
            # ActionChains(driver).click(click_btn).perform()
            element = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'hdcontent')))

            retrytimes = 20
            data_hd = None
            while retrytimes > 0:
                time.sleep(60*1)
                html = driver.page_source
                bf = BeautifulSoup(html, 'html.parser')
                data_hd = trans(bf)
                retrytimes -= 1
                if data_hd:
                    driver.close()
                    return data_hd
            driver.close()
            return None
        except Exception:
            print('错误发生，重新尝试获取，剩余次数{}'.format(retry_count-1))
            retry_count -= 1
            driver.close()
    # delete_proxy(proxy)
    # print('代理节点：{}：{}不可用，已删除'.format(IP, PORT))
    return None


def trans(a):
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
                zhandian.append(d_str.strip())
        data_hd.append(zhandian)

    return data_hd


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def write_data(data, f_str):
    # if data1 is None:
    #     dizhi = []
    #     shijian = []
    # else:
    #     dizhi = [x[3] for x in data1]  # 记录已有地址和时间
    #     shijian = [x[4] for x in data1]
    # 使用列表解析读取二维列表的单独列  [x[0] for x in data]

    path2 = os.path.join(path1, '水利部-新版数据', f_str)
    folder = os.path.exists(path2)
    if not folder:
        os.makedirs(path2)

    # 新爬取结果与旧数据对比，将更新的结果写入文件
    if f_str == '大江大河':
        for hang in data:
            if '\n您所查询数据不存在！！！\n' == hang[0]:
                break
            path3 = os.path.join(path1, '水利部-新版数据', f_str, hang[0])
            folder = os.path.exists(path3)
            if not folder:
                os.makedirs(path3)
            with open(path3 + '\\{}-{}-{}.txt'.format(hang[1], hang[2], hang[3]),
                              'a+',encoding='utf-8') as f:
                f.write('{}\t{}\t{}\t{} \n'.format(time.strftime("%Y-", time.localtime()) + hang[4],
                                                           hang[5], hang[6], hang[7]))

    return data


def time_sleep():
    print('{}数据爬取完成'.format(time.strftime("%m-%d-%H", time.localtime())))
    now = datetime.datetime.now()
    sleep_time = 3600*8 + random.uniform(10, 100)
    end = now + datetime.timedelta(days=sleep_time / 86400)
    print('开始休眠，将休眠至：{}'.format(end))
    time.sleep(sleep_time)


if __name__ == '__main__':
    path1 = os.path.abspath('.')  # 获取当前脚本所在的路径
    folder = os.path.exists(path1 + '\\水利部-新版数据')
    if not folder:
        os.makedirs(path1 + '\\水利部-新版数据')
    print('爬虫开始运行')
    # time.sleep(3600*9)
    url = 'http://xxfb.mwr.cn/sq_djdh.html'
    # a_ex = None
    # while a_ex is None:
    #     a_ex = get_data(url)
    #
    # hd_ex = write_data(a_ex, '大江大河')
    # time_sleep()

    # 主循环，保留
    flag = 1
    while True:
        a = None
        while a is None:
            a = get_data(url)
        hd_ex = write_data(a, '大江大河') # 简单起见，不设置新旧数据对比
        time_sleep()
        if flag % 6 == 1:
            run_stage = '时间：' + time.strftime("%Y-%m-%d-%H", time.localtime()) + '抓取完成'
            email_send(run_stage, time.strftime("%Y-%m-%d-%H", time.localtime()))
        flag = flag + 1





