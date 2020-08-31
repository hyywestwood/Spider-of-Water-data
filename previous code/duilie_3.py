# -*- coding: utf-8 -*-
# @Time    : 2019/5/17 16:04
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : duilie_3.py
# @Software: PyCharm
import multiprocessing
import time


class SubsubProc(multiprocessing.Process):
    def __init__(self):
        super(SubsubProc, self).__init__(name = 'SubsubProc')
        self.daemon = True
    def run(self):
        while True:
            print('this is subsubproc')
            time.sleep(2)

class SubProc(multiprocessing.Process):
    def __init__(self):
        super(SubProc, self).__init__(name = 'SubProc')
        self.daemon = False
    def run(self):
        subsubproc = SubsubProc()
        subsubproc.start()
        while True:
            print('this is SubProc')
            time.sleep(1)

def main():
    subproc = SubProc()
    subproc.start()

    time.sleep(3)

    subproc.terminate()
    subproc.join()
    print('subproc terminated')

    # time.sleep(3600)
if __name__ == '__main__':
    main()