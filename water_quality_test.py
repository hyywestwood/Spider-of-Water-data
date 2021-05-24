from water_data_spider import Spider
import requests,json,time,os,re
import logging, schedule
from waterdata import Water_data_spider

class water_quality(Water_data_spider):
    def __init__(self):
        self.baseurl = 'http://106.37.208.243:8068/GJZ/Ajax/Publish.ashx'
        self.baseheader = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Referer': 'http://106.37.208.243:8068/GJZ/Business/Publish/RealDatas.html',
        } 
        self.post_data = {
            'AreaID': '', 
            'RiverID': '',
            'MNName': '',
            'PageIndex': '-1',
            'PageSize': '60',
            'action': 'getRealDatas',
        }
        self.base_dir = os.path.join(os.getcwd(), '水质数据')
        self.make_dir(self.base_dir)
        
        self.data = None
        self.logger = self.log_setting()
    
    def run(self):
        schedule.every(4).hours.do(self.single_run)
        text = '水质数据爬取完成'
        subject = '水质数据'
        schedule.every(3).days.at("22:30").do(self.email_send, text, subject)
        while True:
            schedule.run_pending()

    def single_run(self):
        self.data = self.get_realdata()
        self.data = self.dict_trans(self.data)
        self.write_data(self.data)
    
    def write_data(self, data):
        for hang in data:
            file_dir = os.path.join(self.base_dir, hang[0])
            self.make_dir(file_dir)
            with open(os.path.join(file_dir, '{}-{}.txt'.format(hang[1], hang[2])), 'a+', encoding='utf-8') as f:
                f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t \n'.format(time.strftime("%Y-", time.localtime()) + hang[3],
                                                    hang[4], hang[5],hang[6],hang[7],hang[8],hang[9],hang[10],hang[11],hang[12],hang[13],
                                                                                             hang[14],hang[15],hang[16]))

    def get_realdata(self):
        res = requests.post(url=self.baseurl, headers=self.baseheader, data=self.post_data)
        real_data = json.loads(res.content)
        return real_data
    
    # 整理数据，去除空格和非法字符
    def dict_trans(self, real_data):
        clean_data = []
        for sta in real_data['tbody']:
            sta_info = []
            for i in range(len(sta)):
                info = sta[i]
                if info is None:
                    info = ''
                if 'span' in info:
                    pattern = r'>.*?</'
                    info = re.findall(pattern, info)[0][1:-2]
                if i != 3:
                    info = info.strip()
                    info = re.sub(r'[\/\\:*?"<>|]', '', info)  # 去除字符中的非法字符
                sta_info.append(info)
            clean_data.append(sta_info)
        return clean_data


if __name__ == '__main__':
    spider = water_quality()
    # spider.single_run() # 测试
    spider.run()
    