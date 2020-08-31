# -*- coding: utf-8 -*-
# @Time    : 2019/5/17 15:36
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : duilie_2.py
# @Software: PyCharm
import multiprocessing
import sys
import time


class Process(multiprocessing.Process):
    def __init__(self, daemon):
        super(Process, self).__init__()
        self.daemon = daemon
    def run(self):
        while True:
            print('in Process')
            print('2222')
            time.sleep(1)

def main():
    process = Process(True)
    process.start()

    time.sleep(5)

    print('main exit now')
    sys.exit(0)

if __name__ == '__main__':
    main()