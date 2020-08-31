# -*- coding: utf-8 -*-
# @Time    : 2019/5/17 16:42
# @Author  : hyy
# @Email   : 1554148540@qq.com
# @File    : duilie_5.py
# @Software: PyCharm
import multiprocessing
import time

event = multiprocessing.Event()


def xiao_fan(event):
    print('生产...')
    print('售卖...')
    # time.sleep(1)
    print('等待就餐')
    event.set()
    event.clear()
    event.wait()
    print('谢谢光临')


def gu_ke(event):
    print('准备买早餐')
    event.wait()
    print('买到早餐')
    print('享受美食')
    # time.sleep(2)
    print('付款，真好吃...')
    event.set()
    event.clear()


if __name__ == '__main__':
    # 创建进程
    xf = multiprocessing.Process(target=xiao_fan, args=(event,))
    gk = multiprocessing.Process(target=gu_ke, args=(event, ))
    # 启动进程
    gk.start()
    xf.start()
    # time.sleep(2)