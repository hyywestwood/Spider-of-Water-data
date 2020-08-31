# -*- coding: utf-8 -*-
# @Time    : 2019/5/17 15:09
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : duilie_1.py
# @Software: PyCharm
import sys
import threading
import time


class Thread(threading.Thread):
    def __init__(self, daemon):
        super(Thread, self).__init__()
        self.daemon = daemon
        print('初始化完成')
    def run(self):
        while True:
            print ('in Thread')
            time.sleep(1)

def main():
    thread = Thread(True)
    print('222222222222')
    thread.start()

    time.sleep(5)

    print ('main exit now')
    sys.exit(0)


if __name__ == '__main__':
    main()