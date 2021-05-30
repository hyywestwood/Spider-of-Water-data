import requests,json,time,os,re
from contextlib import closing
import logging, schedule
import smtplib, configparser
from email.mime.text import MIMEText
from email.header import Header

class Water_data_spider():
    def __init__(self):
        self.baseurl = 'http://xxfb.mwr.cn/sq_djdh.html'
        self.baseheader = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        } 
        self.base_dir = os.path.join(os.getcwd(), '水利部新版数据')
        self.make_dir(self.base_dir)
        self.data_type_list = ['大江大河', '大型水库', '重点雨水情', '全国日雨量']
        for i in range(len(self.data_type_list)):
            self.make_dir(os.path.join(self.base_dir, self.data_type_list[i]))

        self.url_list = [
            'http://xxfb.mwr.cn/sq_djdh.html',
            'http://xxfb.mwr.cn/sq_dxsk.html',
            'http://xxfb.mwr.cn/sq_zdysq.html'
        ]
        self.target_list = [
            'http://xxfb.mwr.cn/hydroSearch/greatRiver',
            'http://xxfb.mwr.cn/hydroSearch/greatRsvr',
            'http://xxfb.mwr.cn/hydroSearch/pointHydroInfo'
        ]
        self.data = None
        self.cookie = self.get_cookie()
        self.logger = self.log_setting()
    
    def run(self):
        schedule.every().day.at("09:00").do(self.get_qgryl,'http://xxfb.mwr.cn/sq_qgryl.html',\
            'http://xxfb.mwr.cn/hydroSearch/nationalDailyRainfall')
        schedule.every().day.at("09:00").do(self.single_run)
        schedule.every().day.at("21:00").do(self.single_run)
        text = '水利数据爬取完成'
        subject = '水利数据'
        schedule.every(3).days.at("22:00").do(self.email_send, text, subject)
        # schedule.every(2).day.at("22:00").do(self.email_send, text, subject)
        while True:
            schedule.run_pending()
        # self.single_run()
        # self.get_qgryl(
        #     'http://xxfb.mwr.cn/sq_qgryl.html', 
        #     'http://xxfb.mwr.cn/hydroSearch/nationalDailyRainfall',
        #     self.cookie
        # )
    
    # 抓取大江大河，大型水库，重点雨水情
    def single_run(self):
        for i in range(3):
            time.sleep(10)
            try:
                self.data = self.get_data(self.url_list[i], self.target_list[i], self.cookie, self.data_type_list[i])
                self.data = self.dict_trans(self.data)
                self.write_data(self.data, self.data_type_list[i])
                self.logger.info(self.data_type_list[i] + '数据抓取成功')
            except Exception as e:
                # self.logger.info(self.data_type_list[i] + '数据抓取失败')
                self.logger.exception(self.data_type_list[i] + '数据抓取失败')
                # print(e)

    # 获取cookie
    def get_cookie(self):
        if 'Referer' in self.baseheader:
            del self.baseheader['Referer']

        res = requests.get(url=self.baseurl, headers=self.baseheader)
        cookie = res.cookies.get_dict()
        return cookie
    
    def get_data(self, refer_url, target_url, cookie, data_type):
        self.baseheader['Referer'] = refer_url
        if data_type == '大型水库' or data_type == '重点雨水情':
            po = requests.post(url=target_url, headers=self.baseheader, cookies=cookie)
        else:
            po = requests.get(url=target_url, headers=self.baseheader, cookies=cookie)
        data = json.loads((po.content.decode()))['result']
        return data
    
    # 下载全国日雨量图片
    def get_qgryl(self, refer_url, target_url):
        self.cookie = self.get_cookie() # 下载全国日雨量时，更新cookie
        self.baseheader['Referer'] = refer_url
        file_path = os.path.join(self.base_dir, '全国日雨量')
        with closing(requests.get(url=target_url, headers= self.baseheader, cookies=self.cookie, stream=True, timeout=120)) as response:
            chunk_size = 1024 # 单次请求最大值
            with open(os.path.join(file_path, time.strftime("%Y-%m-%d", time.localtime()) + '.png'), "wb") as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
        # print('全国日雨量数据抓取成功')
        self.logger.info('全国日雨量数据抓取成功')
        time.sleep(10)
    
    # 写文件
    def write_data(self, data, data_type):
        for item in data['data']:
            file_path = os.path.join(self.base_dir, data_type, item['poiBsnm'])
            self.make_dir(file_path)
            with open(os.path.join(file_path, '{}-{}-{}.txt'.format(item['poiAddv'], item['rvnm'], item['stnm'])), \
                'a+', encoding='utf-8') as f:
                if data_type == '大江大河':
                    f.write('{}\t{}\t{}\t{} \n'.format(item['tm'], item['zl'], item['ql'], item['wrz']))
                elif data_type == '大型水库':
                    f.write('{}\t{}\t{}\t{}\t{} \n'.format(item['tm'], item['rz'], item['wl'], item['inq'], item['damel']))
                else:
                    f.write('{}\t{}\t{}\t \n'.format(item['tm'], item['dyp'], item['wth']))
        # pass
    # 生成文件夹
    def make_dir(self, file_path):
        folder = os.path.exists(file_path)
        if not folder:
            os.mkdir(file_path)
    
    # 整理数据，去除空格和非法字符
    def dict_trans(self, data):
        for item in data['data']:
            for key in item:
                if isinstance(item[key], str):
                    item[key] = item[key].strip() # 去除字符的前后空格
                    item[key] = re.sub(r'[\/\\:*?"<>|]', '', item[key])  # 去除字符中的非法字符
                    # print(item[key])
        return data
    
    # 日志文件设置
    def log_setting(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler("log.txt")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addHandler(console)
        return logger
    
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
            smtpObj = smtplib.SMTP(mail_host, 25)
            # smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException:
            self.logger.exception("Error: 无法发送邮件")



if __name__ == '__main__':
    spider = Water_data_spider()
    spider.run()
    
